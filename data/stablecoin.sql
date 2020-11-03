-- START:   'Tuesday, September 01 12:00 UTC' (epoch=1598961600, batchId=5329872)
-- END:   'Tuesday, September 29 12:00 UTC' (epoch=1601380800, batchId=5337936)
WITH 
constants (start_time, start_batch, end_time, end_batch, num_tokens_required, min_deposit_amount) as (
    values (
        CAST('2020-09-01 12:00:00' as TIMESTAMP), /* start_time */
        5329872, /* start_batch */
        CAST('2020-09-29 12:00:00' as TIMESTAMP), /* end_time */
        5337936, /* end_batch */
        4, /* num_tokens_required */
        5000 /* min_deposit_amount */
    )
),
token as (
    SELECT * FROM (VALUES
        (decode('6b175474e89094c44da98b954eedeac495271d0f', 'hex'), 7, 18), -- DAI
        (decode('dac17f958d2ee523a2206206994597c13d831ec7', 'hex'), 2, 6), -- USDT
        (decode('a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'hex'), 4, 6), -- USDC
        (decode('8e870d67f660d95d5be530380d0ec0bd388289e1', 'hex'), 5, 18), -- PAX
        (decode('57Ab1ec28D129707052df4dF418D58a2D46d5f51', 'hex'), 66, 18) -- sUSD
    ) as t (address, id, decimals)
),
orders as (
    SELECT 
        FLOOR(EXTRACT(epoch FROM evt_block_time) / 300) AS batch_id,
        owner,
        index as order_id,
        sell_token.id as sell_token_id,
        buy_token.id as buy_token_id
        -- 10^(sell_token.decimals-buy_token.decimals) * "priceNumerator" / "priceDenominator" as price_numerator
    FROM constants, gnosis_protocol."BatchExchange_evt_OrderPlacement" o
    JOIN token sell_token
        ON sell_token.id = o."sellToken" -- Filter: Make sure is one of the challenge tokens
    JOIN token buy_token
        ON buy_token.id = o."buyToken" -- Filter: Make sure is one of the challenge tokens
    WHERE
        -- Rather relax way of checking the liquidity orders
        -- year 2030: 6,311,520
         "validUntil" > 6311520 
         
         -- unlimited
         AND ("priceNumerator" > 3.402823669209384e+38 OR "priceDenominator" > 3.402823669209384e+38)
         
         -- Challenge tokens (filtered in JOIN)
         
         -- spread <= 0.3%
         AND 10^(sell_token.decimals-buy_token.decimals) * "priceNumerator" / "priceDenominator" <= 1.00301
         
         AND evt_block_time < constants.end_time
),
deletions as (
    SELECT 
        DISTINCT owner, order_id, batch_id
    FROM (
        SELECT 
            owner, id as order_id, FLOOR(EXTRACT(epoch FROM evt_block_time) / 300) AS batch_id 
        FROM gnosis_protocol."BatchExchange_evt_OrderDeletion", constants 
        WHERE 
            0=0
            AND evt_block_time < constants.end_time
        UNION
        SELECT owner, id as order_id, FLOOR(EXTRACT(epoch FROM evt_block_time) / 300) AS batch_id 
        FROM gnosis_protocol."BatchExchange_evt_OrderCancellation", constants 
        WHERE 
            0=0
            AND evt_block_time < constants.end_time
    ) c
),
active_orders as (
    SELECT
        orders.batch_id,
        orders.owner,
        orders.order_id,
        sell_token_id,
        buy_token_id,
        deletions.batch_id as batch_id_deleted
    FROM constants, orders
    LEFT OUTER JOIN deletions
        ON orders.owner = deletions.owner
        AND orders.order_id = deletions.order_id
    -- Deleted before the challenge started
    WHERE
        -- Active orders
        deletions.batch_id IS NULL 
        -- OR Deleted orders, that were active at least partially during the challenge
        OR deletions.batch_id > constants.start_batch
),
candidates as (
    SELECT
        owner as address
        --COUNT(*) count
    FROM constants, (
        SELECT DISTINCT
            owner,
            sell_token_id as token_id -- Sell token is enough (so no need to check buy token). The user has to create ALL the combinations A-B, B-A, ...
        FROM active_orders
    ) t
    GROUP BY owner, constants.num_tokens_required
    -- Minimun of 4 tokens
    HAVING COUNT(*) >= constants.num_tokens_required
),
balances AS (
    SELECT
        batch_id,
        trader,
        token,
        SUM(balance) as balance
    FROM gnosis_protocol.view_movement, constants
    WHERE 
        0 = 0
        AND batch_id BETWEEN constants.start_batch AND constants.end_batch -- from "challenge-start" until "challenge-end"
        AND token IN ( SELECT address FROM token)
        AND trader IN (SELECT address FROM candidates)
    GROUP BY batch_id, trader, token
),
balances_per_batch as (
    -- Calculate the balance for the challenge (sum of all tokens) per batch
    SELECT 
        *,
        SUM(amount) OVER (
            PARTITION BY trader
            ORDER BY batch_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as balance
    FROM (
        -- Calculate the balance changes of the relevant tokens
        SELECT
            batch_id,
            trader,
            SUM(amount) as amount -- We sum the amounts of different tokens, cause they are stable coins, so it's fine
        FROM constants, gnosis_protocol.view_movement
        WHERE 
            0 = 0
            --AND batch_id BETWEEN constants.start_batch AND constants.end_batch -- from "challenge-start" until "challenge-end"
            AND batch_id <= constants.end_batch
            AND token IN ( SELECT address FROM token)
            AND trader IN (SELECT address FROM candidates)
        GROUP BY batch_id, trader
    ) b
),
balances_start AS (
    SELECT
        start_batch as batch_id, -- first batch of challenge
        trader,
        balance
    FROM (
        SELECT
            constants.start_batch,
            trader,
            --SUM(balance) as balance,
            balance,
            RANK() OVER (
                PARTITION BY trader
                ORDER BY batch_id DESC
            ) as rank 
        FROM balances_per_batch, constants
        WHERE 
            0 = 0
            -- Get the balance the user had when the challenge started
            AND batch_id <= constants.start_batch
    ) b 
    WHERE rank = 1
),
balance_ranges AS (
    SELECT 
        b.*,
        COALESCE(LEAD (batch_id, 1) OVER (
            PARTITION BY trader
            ORDER BY batch_id
        ), constants.end_batch) batch_id_next
    FROM (
        (
            -- Balances at the first batch of the challenge
            SELECT * FROM balances_start
        ) UNION (
            -- Balances during the challenge
            SELECT 
                batch_id, trader, balance
            FROM balances_per_batch, constants
            WHERE 
                -- Discard balances that are before the challenge. We cannot filter earlier, cause we need to calculate it since the first deposit of the user
                batch_id > constants.start_batch
            ORDER BY batch_id
        )
    ) as b, constants
),
scores_batch AS (
    SELECT
        batch_id,
        trader,
        balance,
        CASE
            WHEN balance < constants.min_deposit_amount THEN 0
            ELSE (batch_id_next - batch_id) * balance
        END as score
    FROM constants, balance_ranges
),
scores AS (
    SELECT 
        trader,
        SUM(score) as score
    FROM scores_batch
    WHERE score > 0 
    GROUP BY trader
),
max_score AS (
    SELECT 
        SUM(score) as sum
    FROM scores
), 
ranking as (
    SELECT 
        RANK() OVER (ORDER BY scores.score DESC) as position,
        CONCAT('0x', ENCODE(scores.trader, 'hex')) as trader,
        scores.score / 8064 as score, -- 8,064: number of batches
        CAST(1000 * scores.score / sum as DECIMAL(18,4)) as gno_estimation,
        scores.score as score_raw,
        scores.trader as trader_hex
    FROM scores, max_score
),
current_balance as (
    SELECT
        trader,
        balance
    FROM (
        SELECT
        trader,
        balance,
        RANK() OVER (
            PARTITION BY trader
            ORDER BY batch_id DESC
        ) as rank 
        FROM balance_ranges
    ) b WHERE rank = 1 -- AND balance > 0
),
lp_trades as 
    (SELECT
        block_time,
        trader_hex, 
        order_id,
        buy_amount,
        sell_amount
    FROM constants, gnosis_protocol."view_trades" as trades
    JOIN gnosis_protocol."BatchExchange_evt_OrderPlacement" as orders
        ON trades.order_id = orders.index
        AND trades.trader_hex = orders.owner
    WHERE revert_time is NULL
    AND orders."buyToken" in (SELECT id FROM token)
    AND orders."sellToken" in (SELECT id FROM token)
    -- TODO: set a meaning value
    AND batch_id >= constants.start_batch
    -- These value rouhgly identify LP orders
    AND orders."validUntil" = 4294967295
    AND orders."priceNumerator" / pow(10, buy_token_decimals) > orders."priceDenominator" / pow(10, sell_token_decimals)
    AND orders."priceNumerator" > 300 * pow(10, 18)
    AND orders."priceDenominator" > 300 * pow(10, 18)),
returns as(
    SELECT 
        trader_hex,
        SUM(buy_amount - sell_amount) as profit,
        COUNT(*) as swaps
    FROM lp_trades
    GROUP BY trader_hex
),
last_gno_price as (
    SELECT price 
    FROM prices."usd_6810e776880c02933d47db1b9fc05908e5386b96"
    ORDER BY minute DESC
    LIMIT 1
),
result as (
SELECT
    position,
    ranking.trader as receiver,
    CASE 
        WHEN score >= 0.01 THEN score
        ELSE 0
    END as score,
    CASE 
        WHEN gno_estimation >= 0.0001 THEN gno_estimation
        ELSE 0
    END as amount,
    score_raw,
    CASE 
        WHEN current_balance.balance > 0.01 THEN current_balance.balance
        ELSE 0
    END as balance,
    COALESCE(profit, 0) as "Profit w/o GNO",
    (COALESCE(profit, 0) / score) * 12 * 100 as "% APR w/o GNO",
    ((COALESCE(profit, 0) + (gno_estimation * last_gno_price.price)) / score) * 12 * 100 as "% APR with GNO",
    COALESCE(swaps, 0) as "# of swaps",
    '0x6810e776880C02933D47DB1b9fc05908e5386b96' as token_address
FROM last_gno_price, ranking
LEFT OUTER JOIN current_balance
    ON ranking.trader_hex = current_balance.trader
LEFT OUTER JOIN returns
    ON ranking.trader_hex = returns.trader_hex
ORDER BY position)

SELECT * FROM result

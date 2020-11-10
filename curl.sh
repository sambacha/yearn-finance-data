curl -H "Accept: application/vnd.github.everest-preview+json" \
    -H "Authorization: token <your-token-here>" \
    --request POST \
    --data '{"event_type": "do-something"}' \
    https://api.github.com/repos/n8ebel/GitHubActionsAutomationSandbox/dispatches


    curl -H "Accept: application/vnd.github.everest-preview+json" \
    -H "Authorization: token <your-token-here>" \
    --request POST \
    --data '{"event_type": "do-something", "client_payload": { "text": "a title"}}' \
    https://api.github.com/repos/n8ebel/GitHubActionsAutomationSandbox/dispatches
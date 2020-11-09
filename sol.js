var solc = require('solc');
//var smt = require('smtsolver');
const smt = require('smtlib');
// Note that this example only works via node and not in the browser.

var input = {
  language: 'Solidity',
  sources: {
    'test.sol': {
      content: 'pragma experimental SMTChecker; contract C { function f(uint x) public { assert(x > 0); } }'
    }
  }
};

var output = JSON.parse(
  solc.compile(JSON.stringify(input), { smtSolver: smt.smtSolver })
);

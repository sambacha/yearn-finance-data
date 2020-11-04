#!/bin/bash
tree -F -H yearn-finance-data > index.html
tree -FL 3 -H yearn-finance-data | grep -v /$ > grep.html

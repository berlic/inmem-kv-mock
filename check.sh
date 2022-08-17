#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

IS_ERROR=0

echo "Styling checks:"
pycodestyle *.py
if [ $? -eq 0 ]; then
  echo "OK!"
else
  IS_ERROR=1
fi

echo ""
echo "Unit tests:"
coverage run --source . -m unittest -v test_*.py
if [ $? -ne 0 ]; then
  IS_ERROR=1
fi

echo ""
echo "Code coverage:"
coverage report -m --omit 'test*'

[ $IS_ERROR -eq 0 ] || exit 1

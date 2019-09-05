#!/usr/bin/env bash
set -exuo pipefail

# Node.js
node --version

# Python
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
python --version

# Java
java --version

# PHP
phpenv versions

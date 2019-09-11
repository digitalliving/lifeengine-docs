#!/usr/bin/env bash
set -exuo pipefail

bundle install


# Prepare raml2markdown
cd raml2markdown
npm install

# Fix running node via shebang on Linux - developers on macs are the worst
sed -Ei 's@env node --harmony@env node@' node_modules/.bin/*
sed -Ei 's@env node --harmony@env node@' node_modules/oas-raml-converter/lib/bin/*

cd ..

# Install all the dependencies required to
# generate and validate code examples based
# on API specification in `raml2markdown/src`.
bash scripts/code-examples/install-deps.sh


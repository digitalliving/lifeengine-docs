#!/usr/bin/env bash
set -exuo pipefail

bundle install

# Prepare raml2markdown
cd raml2markdown
npm install
cd ..

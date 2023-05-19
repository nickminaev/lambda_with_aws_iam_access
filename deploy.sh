#!/bin/sh
terraform init
[ -f package.zip ] && rm -rf package.zip
zip package.zip lambda_function.py
terraform apply
#!/bin/bash

CGO_ENABLED=0 go build -o main main.go
REGISTRY=${REGISTRY:-"localhost:5000/"}

# custom the tag
VERSION="latest"
if [ $# -ne 0 ]; then
  VERSION=$1
fi


cp Pulumi.yaml Pulumi.yaml.bkp
yq -iy '.runtime = {"name": "go", "options": {"binary": "./main"}}' Pulumi.yaml

oras push --insecure \
  "${REGISTRY}examples/deploy:${VERSION}" \
  --artifact-type application/vnd.ctfer-io.scenario \
  main:application/vnd.ctfer-io.file \
  Pulumi.yaml:application/vnd.ctfer-io.file

rm main
mv Pulumi.yaml.bkp Pulumi.yaml

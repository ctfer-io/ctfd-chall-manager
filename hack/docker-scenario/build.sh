#!/bin/bash

CGO_ENABLED=0 go build -o main main.go
REGISTRY=${REGISTRY:-"localhost:5000/"}

cp Pulumi.yaml Pulumi.yaml.bkp
yq -iy '.runtime = {"name": "go", "options": {"binary": "./main"}}' Pulumi.yaml

oras push --insecure \
  "${REGISTRY}examples/docker:latest" \
  --artifact-type application/vnd.ctfer-io.scenario \
  main:application/vnd.ctfer-io.file \
  Pulumi.yaml:application/vnd.ctfer-io.file

rm main
mv Pulumi.yaml.bkp Pulumi.yaml

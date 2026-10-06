#!/bin/sh
set -eu
if [ "${1-}" != "--apply" ]; then
    echo 'Dry run: docker run --rm --platform linux/amd64 ubuntu:24.04 uname -m'
    echo 'Uses the existing engine; no VM changes, host mounts, installers or license activation.'
    exit 0
fi
command -v docker >/dev/null
docker info --format 'Engine: {{.Architecture}} / {{.ServerVersion}}'
docker run --rm --platform linux/amd64 ubuntu:24.04 uname -m

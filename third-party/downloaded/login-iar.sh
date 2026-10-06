#!/bin/sh
# User-run interactive authentication only; never run during image build.
set -eu
if [ ! -t 0 ] || [ ! -t 1 ]; then
  echo 'Run this yourself in a local interactive terminal; do not send credentials or device codes in chat.' >&2
  exit 2
fi
container_name=opencfw-iar-session
image_name=opencfw/iar-base:10.10.2-local
if docker container inspect "$container_name" >/dev/null 2>&1; then
  actual_image=$(docker container inspect --format '{{.Config.Image}}' "$container_name")
  if [ "$actual_image" != "$image_name" ]; then
    echo 'Existing container has a different image; inspect it without overwriting it.' >&2
    exit 2
  fi
  docker start "$container_name" >/dev/null
else
  docker run -d --name "$container_name" --hostname "$container_name" \
    --platform linux/amd64 --cap-drop ALL --security-opt no-new-privileges \
    --mount type=volume,src=opencfw-iar-user-home,dst=/root \
    "$image_name" sleep infinity >/dev/null
fi
# No token, password or API key is an argument. The user follows the displayed
# vendor verification URL and enters the device code in their own browser.
docker exec -it "$container_name" iarlogin login --use-device-code --no-open
# Deliberately do not retrieve/print the access token or license-key material.
docker exec -it "$container_name" iarlogin login-status

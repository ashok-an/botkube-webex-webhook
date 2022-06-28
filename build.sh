#!/bin/bash -x
image="docker.io/ashoka007/botkube-webhook-handler"
version=$1
[[ "$version" == "" ]] && { echo "Usage: $0 <version>"; exit 2; }
docker build -t ${image}:${version} . && docker push ${image}:${version}

 

#!/bin/bash

./torsniff/run.sh

docker run --name torsniffui -v torsniff_data:/torsniff_data -p 1668:1668/tcp -f Dockerfile
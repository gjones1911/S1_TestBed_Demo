#!/bin/bash

docker build -t ilabutk/s1:0.2 -f docker/Dockerfile_fe.s1 .

## to push to hub
# docker push ilabutk/s1:0.2
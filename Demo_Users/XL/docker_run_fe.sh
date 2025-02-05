#!/bin/bash

## local test
docker run --name local_s1 -p 8888:7860  ilabutk/s1:0.1

## PROD
# ```
# sudo docker run -d \
#     --restart always \
#     --name gradio_s1 \
#     --network viridian_network \
#     --env "VIRTUAL_HOST=s1.viridian.ise.utk.edu" \
#     --env "LETSENCRYPT_HOST=s1.viridian.ise.utk.edu" \
#     --env "LETSENCRYPT_EMAIL=ilab.utk@gmail.com" \
#     ilabutk/s1:0.1
# ```
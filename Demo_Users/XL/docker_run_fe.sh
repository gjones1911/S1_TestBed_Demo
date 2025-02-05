#!/bin/bash

## local test: --name local_s1
docker run --rm -p 8888:7860 ilabutk/s1:0.2

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
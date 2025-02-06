# scripts
- FE
    - build: `../docker_build_image_fe.sh`
    - locally run: `docker_run_fe.sh`
    - 
- run PROD mode: 

    - NOT NEEDED -p 7860:7860 \
    - DID NOT have the `s1.DOMAIN` yet
        
    ```sh
        sudo docker run -d \
            --restart always \
            --name gradio_s1 \
            --network viridian_network \
            --env "VIRTUAL_HOST=s1.viridian.ise.utk.edu" \
            --env "LETSENCRYPT_HOST=s1.viridian.ise.utk.edu" \
            --env "LETSENCRYPT_EMAIL=ilab.utk@gmail.com" \
            ilabutk/s1:0.1
    ```
- Production mode
    - Scalable & reliable solutions 
        - Grafana, InfluxDB
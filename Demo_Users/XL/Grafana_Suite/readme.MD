# log
- grafana - mosquitto - telegraf - mysql
- `docker compose up -d`
- `docker compose down -v` | nuke      
- `docker exec -it mosquitto /bin/bash`
    - `touch password_file`
        - add "admin:secret!99"
    - chmod 0700 /password_file
    - `mosquitto_passwd -U password_file`

## links
- http://localhost:3000/login works
```sh

    # So far, has to allow to make Mosquitto work :DANGER:
    # Allow anonymous access (set to false in production)
    allow_anonymous true

    ## Test this inside mosquitto docker:
    mosquitto_sub -h localhost -t sensors/temperature -v

    #inside influxdb
    influx auth create --org ASL --all-access

    docker logs influxdb | grep "token"

    curl --request POST "http://localhost:8086/api/v2/authorizations" \
        --header "Content-Type: application/json" \
        --data '{
            "org": "ASL",
            "description": "Telegraf Token",
            "permissions": [
            { "action": "read", "resource": { "type": "buckets" }},
            { "action": "write", "resource": { "type": "buckets" }}
            ]
        }'



    # 
    curl -G http://localhost:8086/query --data-urlencode "q=SHOW DATABASES"

```
- https://grafana.com/tutorials/stream-metrics-from-telegraf-to-grafana/
- add service account: grafana_sa
    - glsa_8py2p8OWZZmGyNvrjXOxGuvdCD0Opbei_0cf34ffa
    - sa-1-grafana_sa-8243bf79-d0d0-4235-97c2-94ab45b406c0	


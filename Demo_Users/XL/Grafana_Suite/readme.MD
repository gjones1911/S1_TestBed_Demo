# log
- grafana - mosquitto - telegraf - mysql
- `docker compose up -d`
- `docker compose down -v` | nuke      
- `docker exec -it mosquitto /bin/bash`
    - `touch password_file`
        - add "admin:secret!99"
    - chmod 0700 /password_file
    - `mosquitto_passwd -U password_file`

 -   username = "hivemquser" # admin  
  password = "mqAccess2024REC"

  hivemquser:mqAccess2024REC
- docker-compose.s1.yml 
    - for viz on the s1 testbed computer
    - Grafana suite

## links
- http://localhost:3000/login works
```sh

    # So far, has to allow to make Mosquitto work :DANGER:
    # Allow anonymous access (set to false in production)
    allow_anonymous true

    ## Test this inside mosquitto docker:
    mosquitto_sub -h localhost -t sensors/temperature -v

    #inside influxdb -> v.18 only
    - no api



    # 
    curl -G http://localhost:8086/query --data-urlencode "q=SHOW DATABASES"

```
- https://grafana.com/tutorials/stream-metrics-from-telegraf-to-grafana/
- add service account: grafana_sa



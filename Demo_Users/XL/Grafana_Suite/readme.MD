# log
- grafana - mosquitto - telegraf - mysql
- `docker compose up -d`
- `docker exec -it mosquitto /bin/bash`
    - `touch password_file`
        - add "admin:secret!99"
    - chmod 0700 /password_file
    - `mosquitto_passwd -U password_file`

## links
- http://localhost:3000/login

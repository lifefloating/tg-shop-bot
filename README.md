docker build --network host  -t greed .

docker run -p port:port -v /home/config/config.toml:/etc/greed/config.toml --name greed greed


docker run -p 8080:8080 -v /var/lib/TGgreed/:/var/lib/TGgreed/ -d --name greed greed
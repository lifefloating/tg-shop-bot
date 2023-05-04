docker build --network host  -t greed .

docker run -p port:port -v /home/config/config.toml:/etc/greed/config.toml --name greed greed
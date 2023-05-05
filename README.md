docker build --network host  -t greed .

docker run -p port:port -v /home/config/config.toml:/etc/greed/config.toml --name greed greed


docker run -p 8080:8080 -v /var/lib/TGgreed/:/var/lib/TGgreed/ -d --name greed greed


<!-- TODO -->
充值入口关闭，所有人账户基本等于0，下单点完成 直接谈支付方式 三种支付 三个二维码 选择哪个出哪个二维码 不管支付状态，下面弹出输入收货信息的口
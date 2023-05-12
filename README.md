docker build --network host  -t greed .

docker run -p port:port -v /home/config/config.toml:/etc/greed/config.toml --name greed greed

/var/lib/TGgreed/ sqlite文件
docker run -p 8080:8080 -v /var/lib/TGgreed/:/var/lib/TGgreed/ -d --name greed greed


<!-- TODO -->
充值入口关闭，所有人账户基本等于0，下单点完成 直接谈支付方式 三种支付 三个二维码 选择哪个出哪个二维码 不管支付状态，下面弹出输入收货信息的口

商品展示先展示几条，剩下的翻页显示

下载excel数据改成order

1. 交易清单，编辑经理隐藏
2. 欢迎信息下面增加一个开始购物，我的订单，和频道 客服 总共两行
3. 开始购物是跳转网页，网页内完成下单 支付
4. 隐藏我的订单，语言，商品列表
5. 下载excel数据改成order
6. 网页内需要 商品列表，加入购物车，购物车列表，订单列表，创建订单
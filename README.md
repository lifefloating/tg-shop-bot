docker build --network host  -t greed .

/var/lib/TGgreed/ sqlite文件
docker run -p 8080:8080 -v /var/lib/TGgreed/:/var/lib/TGgreed/ -d --name greed greed

/ 前端docker
docker run --name my-nginx -p 888:80 -v /home/gitCode/tg-shop-mall/dist/:/usr/share/nginx/html:ro -d nginx


商品展示先展示几条，剩下的翻页显示

下载excel数据改成order

1. 交易清单，编辑经理隐藏
2. 欢迎信息下面增加一个开始购物，我的订单，和频道 客服 总共两行
3. 开始购物是跳转网页，网页内完成下单 支付
4. 隐藏我的订单，语言，商品列表
5. 下载excel数据改成order
6. 网页内需要 商品列表，加入购物车，购物车列表，订单列表，创建订单
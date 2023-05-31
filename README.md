docker build --network host  -t greed .

/var/lib/TGgreed/ sqlite文件
docker run -p 8080:8080 -v /var/lib/TGgreed/:/var/lib/TGgreed/ -d --name greed greed

/ 前端docker
docker run --name my-nginx -p 888:80 -v /home/gitCode/tg-shop-mall/dist/:/usr/share/nginx/html:ro -d nginx


商品展示先展示几条，剩下的翻页显示

下载excel数据改成order

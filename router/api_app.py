from flask import Blueprint
from flask import request
from flask import send_from_directory
from controller.api_worker import api_worker
from utils import wrap_resp

web_service_app = Blueprint(
    'api_app', __name__, url_prefix='/api')


@web_service_app.route(
    '/ping', methods=['GET'])
@wrap_resp
def ping():
    return 'hello'

# 加入购物车
@web_service_app.route('/addCart', methods=['POST'])
@wrap_resp
def add_cart():
    params = request.get_json(force=True)
    return api_worker.add_cart(params)

# 移除购物车
@web_service_app.route('/removeCart', methods=['POST'])
@wrap_resp
def remove_cart():
    params = request.get_json(force=True)
    return api_worker.remove_cart(params)

# 购物车列表
@web_service_app.route('/cartList', methods=['POST'])
@wrap_resp
def cart_list():
    params = request.get_json(force=True)
    return api_worker.cart_list(params)

# 订单列表
@web_service_app.route('/orderList', methods=['POST'])
@wrap_resp
def order_list():
    params = request.get_json(force=True)
    return api_worker.order_list(params)

# 商品列表
@web_service_app.route('/productList', methods=['POST'])
@wrap_resp
def product_list():
    # params = request.get_json(force=True)
    return api_worker.product_list()

# 搜索商品
@web_service_app.route('/productSearch', methods=['POST'])
@wrap_resp
def search_products():
    params = request.get_json(force=True)
    return api_worker.search_products(params)

# 商品详情
@web_service_app.route('/productDetail', methods=['POST'])
@wrap_resp
def product_detail():
    params = request.get_json(force=True)
    return api_worker.product_detail(params)


# 创建订单
@web_service_app.route('/order', methods=['POST'])
@wrap_resp
def create_order():
    params = request.get_json(force=True)
    return api_worker.create_order(params)

# 轮播图
@web_service_app.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory('static/images', filename)
from flask import Blueprint
from flask import request
from controller.api_worker import api_worker
from utils import wrap_resp

web_service_app = Blueprint(
    'api_app', __name__, url_prefix='/api')


@web_service_app.route(
    '/ping', methods=['GET'])
@wrap_resp
def ping():
    return 'hello'

# TODO
# 加入购物车
# 购物车列表
# 订单列表
# 创建订单


# 加入购物车
@web_service_app.route('addCart', methods=['POST'])
@wrap_resp
def add_cart():
    params = request.get_json(force=True)
    return  api_worker.add_cart(params)

# 移除购物车
@web_service_app.route('removeCart', methods=['POST'])
@wrap_resp
def remove_cart():
    params = request.get_json(force=True)
    return  api_worker.remove_cart(params)

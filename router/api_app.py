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



@web_service_app.route('posttest', methods=['POST'])
@wrap_resp
def post_test():
    params = request.get_json(force=True)
    return  api_worker.post_method(params)

@web_service_app.route('gettest', methods=['GET'])
@wrap_resp
def get_test(id):
    return api_worker.get_method(id)
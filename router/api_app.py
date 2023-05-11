from flask import Blueprint
from flask import request
from controller.api_worker import api_worker
from utils import wrap_resp

web_service_app = Blueprint(
    'api_app', __name__, url_prefix='/api')


@api_app.route(
    '/ping', methods=['GET'])
@wrap_resp
def ping():
    return 'hello'


@api_app.router('posttest', methods=['POST'])
@wrap_resp
def post_test():
    params = request.get_json(force=True)
    return  api_worker.post_method(params)

@api_app.router('gettest', methods=['GET'])
@wrap_resp
def get_test(id):
    return api_worker.get_method(id)
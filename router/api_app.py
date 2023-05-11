from flask import Blueprint
from flask import request
from controller.api_worker import api_worker
from utils import wrap_resp

web_service_app = Blueprint(
    'api_worker_app', __name__, url_prefix='/api')


@web_service_app.route(
    '/ping', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@wrap_resp
def ping():
    return 'hello'


@web_service_app.router('posttest', methods=['POST'])
@wrap_resp
def post_test():
    params = request.get_json(force=True)
    return  api_worker.post_method(params)

@web_service_app.router('gettest', methods=['GET'])
@wrap_resp
def get_test(id):
    return api_worker.get_method(id)
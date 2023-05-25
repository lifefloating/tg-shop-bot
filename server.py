from flask import Flask, g, request
import os
from flask import jsonify, make_response
from flask_cors import CORS
from urllib import parse
from utils import failReturn
from router.api_app import web_service_app

# flask server
server = Flask(__name__)
CORS(server)

# for file_name in os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/router/'):
#     if file_name.endswith('_app.py'):
#         name = os.path.splitext(file_name)[0]
#         module = importlib.import_module(name)
#         blueprint = getattr(module, name, None)
#         if blueprint is not None:

server.register_blueprint(web_service_app)


# @server.before_request
# def before_request():
#     g.session = db_session()
#     path = request.path
#     if 'Authorization' not in request.headers:
#         response = make_response(
#             json.dumps(falseReturn('NO_AUTHORIZATION')))
#         response.status_code = 400
#         return response

#     if 'X-User-UUID' not in request.headers:
#         response = make_response(
#             json.dumps(falseReturn('NO_USER_INFO')))
#         response.status_code = 401
#         return response

#     authorization = request.headers['Authorization']
#     access_tokenArr = authorization.split(" ")

#     current_dict = {}
#     current_dict['USERUUID'] = request.headers['X-User-UUID']
#     current_dict['ACCESS_TOKEN'] = access_tokenArr[1]

#     g.current = current_dict


# @server.teardown_request
# def teardown_request(exception):
#     g.session.close()


@server.errorhandler(404)
def error_handle_404(error):
    data = jsonify(failReturn('SERVER_ERROR', f"{error}"))
    response = make_response(data)
    response.status_code = 404
    response.headers['Content-Type'] = 'application/json'
    return response


@server.errorhandler(405)
def error_handle_405(error):
    data = jsonify(failReturn('SERVER_ERROR', f"{error}"))
    response = make_response(data)
    response.status_code = 405
    response.headers['Content-Type'] = 'application/json'
    return response


@server.errorhandler(500)
def error_handle_500(error):
    data = jsonify(failReturn('SERVER_ERROR', f"{error}"))
    response = make_response(data)
    response.status_code = 500
    response.headers['Content-Type'] = 'application/json'
    return response
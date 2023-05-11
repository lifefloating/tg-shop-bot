import logging
from functools import wraps
from datetime import datetime
import simplejson as json
from flask import jsonify, make_response, g
from sqlalchemy.ext.declarative import DeclarativeMeta
from exceptions import (HttpException, UnauthorizedException,
                        AccessDeniedException, SQLException)
from schematics.exceptions import ModelConversionError, ModelValidationError


log = logging.getLogger(__name__)

DATE_PATTEN = '%m/%d/%Y %I:%M %p%m/%d/%Y %I:%M %p'

class LCJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Datetime class
        if isinstance(obj, datetime):
            return obj.strftime(DATE_PATTEN)
            # SQLAlchemy class
        elif isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [
                    x for x in dir(obj)
                    if not x.startswith('_') and x != 'metadata'
            ]:

                if hasattr(obj, '_fillable') and obj._fillable \
                        and field not in obj._fillable:
                    continue

                if hasattr(obj, '_hidden') and obj._hidden\
                        and field in obj._hidden:
                    continue

                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, datetime):
                        data = data.strftime(DATE_PATTEN)
                    # this will fail on non-encodable values, like other
                    # classes
                    json.dumps(data)
                    fields[field.upper()] = data
                except TypeError:
                    continue

            return fields
        return json.JSONEncoder.default(self, obj)



def telegram_html_escape(string: str):
    return string.replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("&", "&amp;") \
        .replace('"', "&quot;")


def json_response(data=None, status='SUCCESS'):
    resp = successReturn(data=data, status=status)
    return LCJSONEncoder().encode(resp)

def successReturn(data=None, status='SUCCESS'):
    return {
        "status": status,
        "data": data,
        "desc": '',
    }

def failReturn(status='FAIL', message=None):
    return {
        "status": status,
        "desc": message,
        "data": False
    }


def exception_decorate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (
                ModelConversionError,
                ModelValidationError,
        ) as e:
            log.error(f"model error info {e}")
            data = jsonify(
                failReturn(status='INVALID_PARAMETERS', message=f"{e}"))
            response = make_response(data)
            response.status_code = 400
            return response

        except SQLException as e:
            log.error(f"SQL error info {e.message}")
            data = jsonify(
                failReturn(status='SQL_ERROR', message=f"{e.message}"))
            response = make_response(data)
            response.status_code = e.status_code
            return response

        except UnauthorizedException as e:
            log.error(f"unauthoriztion error info {e.message}")
            data = jsonify(failReturn(e.status, e.message))
            response = make_response(data)
            response.status_code = e.status_code
            return response

        except AccessDeniedException as e:
            log.error(f"access denied error info {e.message}")
            data = jsonify(failReturn(e.status, e.message))
            response = make_response(data)
            response.status_code = e.status_code
            return response

        except HttpException as e:
            log.error(f"other error info {e.message}")
            data = jsonify(failReturn(e.status, e.message))
            response = make_response(data)
            response.status_code = e.status_code
            return response

        except Exception as e:
            traceback.print_exc()
            log.error(f"system error info {e}")
            data = jsonify(failReturn(status='SERVER_ERROR', message=f"{e}"))
            response = make_response(data)
            response.status_code = 500
            return response

    return wrapper


def wrap_resp(func):
    @wraps(func)
    @exception_decorate
    def wrap_decorator(*args, **kwargs):
        resp = func(*args, **kwargs)
        response = make_response(json_response(resp))
        response.status_code = 200
        response.headers['Content-Type'] = 'application/json'
        return response

    return wrap_decorator
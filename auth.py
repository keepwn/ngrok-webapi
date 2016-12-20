from pycnic.errors import HTTPError
from functools import wraps

from model import Auth


class AuthError(HTTPError):

    status_code = 200
    message = "401 Not Authorized"
    data = None
    headers = [['Access-Control-Allow-Origin', '*']]
    def __init__(self):
        super(HTTPError, self).__init__(self.status_code, self.message, self.data, self.headers)

    def response(self):
        return {
            "error": 401,
            "msg": self.message,
            "data": self.data
        }


def requires_auth():
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not verify_auth(args[0].request):
                raise AuthError()
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def verify_auth(request):
    if Auth.select().count() > 0:
        token = request.args.get('token', '')
        try:
            auth = Auth.get(Auth.id == 1)
            return auth.token == token
        except:
            return False
    else:
        return False

def change_auth(old_token, new_token):
    if Auth.select().count() > 0:
        try:
            auth = Auth.get(Auth.id == 1)
            if auth.token == old_token:
                auth.token = new_token
                auth.save()
                return True
            else:
                return False
        except:
            return False
    else:
        return False

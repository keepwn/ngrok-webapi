from pycnic.core import WSGI, Handler
import json
import yaml

from model import database_init
from config import get_config
from core.ngrokmanager import NgrokManager
from core.error import TunnelInstanceError, TunnelManagerError


NM = NgrokManager(get_config('basic', 'docker_url'))


class Info(Handler):

    def get(self):
        return {
            "version": get_config('basic', 'version'),
        }


class Tunnels(Handler):

    def get(self):
        res = NM.list()
        return {'data': res, 'error': 0}

    def post(self):
        try:
            res = NM.create(self.request.data)
            return {'data': res, 'error': 0}
        except TunnelManagerError as e:
            return {'data': None, 'error': 1, 'msg': e.message}

    def delete(self):
        res = NM.clear()
        return {'data': res, 'error': 0}


class Tunnel(Handler):

    def get(self, id):
        try:
            result = NM.get(id)
            return {'data': result, 'error': 0}
        except TunnelManagerError as e:
            return {'data': None, 'error': 1, 'msg': e.message}

    def delete(self, id):
        try:
            result = NM.remove(id)
            return {'data': result, 'error': 0}
        except TunnelManagerError as e:
            return {'data': None, 'error': 1, 'msg': e.message}

    def patch(self, id):
        action = self.request.data.get('action', '')

        msg, result = '', ''
        try:
            if action == 'start':
                result = NM.start(id)
            elif action == 'stop':
                result = NM.stop(id)
            elif action == 'rebuild':
                result = NM.rebuild(id)
        except TunnelManagerError as e:
            msg = e.message

        if msg:
            return {'data': result, 'error': 1, 'msg': msg}
        else:
            return {'data': result, 'error': 0}


class TunnelLog(Handler):

    def get(self, id):
        try:
            offset = int(self.request.args.get('offset', 0))
            limit = int(self.request.args.get('limit', 10))
            tunnel = NM.get_tunnel_instance_by_id(id)
            result = tunnel.log(offset=offset, limit=limit)
            return {'data': result, 'error': 0}
        except TunnelManagerError as e:
            return {'data': None, 'error': 1, 'msg': e.message}


class TunnelStatus(Handler):

    def get(self, id):
        try:
            tunnel = NM.get_tunnel_instance_by_id(id)
            result = tunnel.status()
            if result:
                return {'data': result, 'error': 0}
            return {'data': result, 'error': 1, 'msg': 'tunnel does not running'}
        except TunnelManagerError as e:
            return {'data': None, 'error': 1, 'msg': e.message}


class app(WSGI):
    routes = [
        ("/info", Info()),
        ("/api/tunnels", Tunnels()),
        ("/api/tunnels/([\w]+)", Tunnel()),
        ("/api/tunnels/([\w]+)/log", TunnelLog()),
        ("/api/tunnels/([\w]+)/status", TunnelStatus())
    ]

    database_init()

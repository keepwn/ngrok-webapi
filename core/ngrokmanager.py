from docker import Client
import json
import peewee
import time

from model import Tunnel, tunnel_to_dict
from config import get_config
from core.error import TunnelManagerError
from core.ngrokwrapper import Ngrok, NgrokConfig


class NgrokManager:

    def __init__(self, docker_url):
        self.docker_cli = Client(base_url=docker_url)

    def get_tunnel_instance(self, tunnel):
        ngrok_config = NgrokConfig(
            name=tunnel.name,
            hostname=tunnel.hostname,
            local_addr=tunnel.localaddr,
            remote_port=tunnel.remoteport,
            proto=tunnel.proto,
            auth=tunnel.auth
        )
        tunnel_instance = Ngrok(
            self.docker_cli, ngrok_config, start_time=tunnel.starttime)
        return tunnel_instance

    def get_tunnel_instance_by_id(self, id):
        tunnel = Tunnel.get(Tunnel.id == id)
        return self.get_tunnel_instance(tunnel)

    def update_tunnel_start_time(self, id):
        tunnel = Tunnel.get(Tunnel.id == id)
        tunnel.starttime = int(time.time())
        tunnel.save()
        return tunnel

    def list(self):
        tunnel_dicts = []
        for tunnel in Tunnel.select():
            tunnel_dict = self.get(tunnel.id)
            tunnel_dicts.append(tunnel_dict)

        return tunnel_dicts

    def get(self, id):
        try:
            tunnel = Tunnel.get(Tunnel.id == id)
            tunnel_instance = self.get_tunnel_instance(tunnel)

            tunnel_dict = tunnel_to_dict(tunnel)
            tunnel_dict['state'] = tunnel_instance.state()
            tunnel_dict['status'] = tunnel_instance.status()
            tunnel_dict['exists'] = tunnel_instance.exists()

            return tunnel_dict
        except peewee.DoesNotExist as e:
            raise TunnelManagerError(e, 'id does not exist in db')

    def start(self, id):
        try:
            # update starttime
            tunnel = self.update_tunnel_start_time(id)
            tunnel_instance = self.get_tunnel_instance(tunnel)
            if tunnel_instance.exists():
                tunnel_instance.start()
                return self.get(id)
            else:
                raise TunnelManagerError(None, 'container no exists')
        except peewee.DoesNotExist as e:
            raise TunnelManagerError(e, 'id does not exist in db')

    def stop(self, id):
        try:
            tunnel_instance = self.get_tunnel_instance_by_id(id)
            if tunnel_instance.exists():
                tunnel_instance.stop()
                return self.get(id)
            else:
                raise TunnelManagerError(None, 'container no exists')
        except peewee.DoesNotExist as e:
            raise TunnelManagerError(e, 'id does not exist in db')

    def rebuild(self, id):
        try:
            # update starttime
            tunnel = self.update_tunnel_start_time(id)
            tunnel_instance = self.get_tunnel_instance(tunnel)
            if tunnel_instance.exists():
                tunnel_instance.down()
            tunnel_instance.up()

            return self.get(id)
        except peewee.DoesNotExist as e:
            raise TunnelManagerError(e, 'id does not exist in db')

    def remove(self, id):
        try:
            tunnel = Tunnel.get(Tunnel.id == id)
            tunnel_instance = self.get_tunnel_instance(tunnel)
            if tunnel_instance.exists():
                tunnel_instance.down()
            tunnel.delete_instance()

        except peewee.DoesNotExist as e:
            raise TunnelManagerError(e, 'id does not exist in db')

    def clear(self):
        for tunnel in Tunnel.select():
            self.remove(tunnel.id)

    def create(self, tunnel_dict):
        try:
            print(tunnel_dict)
            new = Tunnel(
                name=tunnel_dict['name'] if tunnel_dict.get(
                    'name', '') else 'default',
                hostname=tunnel_dict.get('hostname', ''),
                localaddr=tunnel_dict.get('localaddr', ''),
                remoteport=tunnel_dict.get('remoteport', ''),
                proto=tunnel_dict.get('proto', ''),
                auth=tunnel_dict.get('auth', ''),
                starttime=0
            )
            # insert new tunnel into db
            new.save()
            # create new tunnel instance
            # if already exist, then rebuild(down and up)
            self.rebuild(new.id)

            return self.get(new.id)
        except peewee.IntegrityError as e:
            raise TunnelManagerError(e, 'tunnel name should be UNIQUE in db')

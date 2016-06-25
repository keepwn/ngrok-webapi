import yaml
import os
import re

from config import get_config
from core.error import TunnelInstanceError


class Ngrok:

    def __init__(self, docker_cli, config, start_time=0):
        self.cli = docker_cli
        self.config = config
        self.name = 'ngrok_' + config.name + '_'
        self.image = 'alpine:latest'
        self.command = config.command()
        self.volumes = config.volumes()
        self.ports = config.ports()

        self.start_time = start_time

    def id(self):
        res = self.cli.containers(all=True, filters={'name': self.name})
        if len(res) > 0:
            return res[0].get('Id')
        return None

    def exists(self):
        container_id = self.id()
        if container_id:
            return True
        return False

    def state(self):
        res = self.cli.containers(all=True, filters={'name': self.name})
        if len(res) > 0:
            return res[0].get('State')
        return None

    def status(self):
        if self.state() != 'running':
            return None

        # get maping url
        mapping = ''
        regex1 = re.compile(r'^.*Tunnel established at(.*?)$', re.MULTILINE)
        matched = regex1.findall(self.__log(self.start_time))
        if matched:
            mapping = matched.pop().strip()

        # get address and port from mapping
        proto = ''
        addr = ''
        port = ''
        regex2 = re.compile(
            r'((?P<proto>http|https|tcp)://)(?P<addr>[a-zA-Z0-9\._-]+\.[a-zA-Z]{2,}):(?P<port>[0-9]{1,5})')
        matched = regex2.search(mapping)
        if matched:
            proto = matched.group('proto')
            addr = matched.group('addr')
            port = matched.group('port')

        info = {}
        info['url'] = mapping
        info['proto'] = proto
        info['addr'] = addr
        info['port'] = port
        return info

    def __log(self, since=0):
        container_id = self.id()
        res = self.cli.logs(
            container=container_id,
            stdout=True,
            stderr=False,
            timestamps=True,
            tail='all',
            since=since
        ).decode()
        return res

    def log(self):
        res = self.__log(self.start_time)
        return res.split('\n')

    def init_config_file(self):
        yaml_path = self.config.yaml_path_in_container
        yaml_dir = os.path.split(yaml_path)[0]
        if not os.path.exists(yaml_dir):
            os.mkdir(yaml_dir)
        
        data = self.config.dump()
        
        with open(yaml_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    def clear_config_file(self):
        yaml_path = self.config.yaml_path_in_container
        if os.path.exists(yaml_path):
            os.remove(yaml_path)

    def create(self):
        '''
        create
        '''
        if self.exists():
            raise TunnelInstanceError(None, 'already exists')

        # init config file
        self.init_config_file()
        # create new container
        container = self.cli.create_container(
            name=self.name,
            image=self.image,
            command=self.command,
            volumes=self.volumes[0],
            host_config=self.cli.create_host_config(binds=self.volumes[1])
        )

        return container.get('Id')

    def remove(self):
        '''
        remove
        '''
        # remove config file
        self.clear_config_file()
        # remove the container
        container_id = self.id()
        if container_id:
            response = self.cli.remove_container(container=container_id)
            print(response)
            return True
        else:
            raise TunnelInstanceError(None, 'container no exists')

    def start(self):
        '''
        start
        '''
        container_id = self.id()
        if container_id:
            response = self.cli.start(container=container_id)
            return True
        else:
            raise TunnelInstanceError(None, 'container no exists')

    def stop(self):
        '''
        stop
        '''
        container_id = self.id()
        if container_id:
            response = self.cli.stop(container=container_id)
            print(response)
            return True
        else:
            raise TunnelInstanceError(None, 'container no exists')

    def up(self):
        '''
        create and start
        '''
        self.create()
        self.start()

    def down(self):
        '''
        stop and remove
        '''
        self.stop()
        self.remove()


class NgrokConfig:

    def __init__(self, name, hostname, local_addr, remote_port, proto, auth):
        # set by app.conf
        self.server_addr = get_config('ngrok', 'server_addr')
        self.trust_host_root_certs = True if get_config(
            'ngrok', 'trust_host_root_certs').lower() in ("true", "1") else False
        self.runtime_dir = get_config('ngrok', 'runtime_dir')
        self.runtime_dir_in_container = get_config(
            'ngrok', 'runtime_dir_in_container')
        self.yaml_dirname = get_config('ngrok', 'yaml_dirname')

        self.name = name

        port_map = {}
        port_map['proto'] = dict([(
            proto if proto else 'http',
            local_addr
        )])
        if proto == 'tcp' and remote_port:
            port_map['remote_port'] = int(remote_port)

        port_map['auth'] = auth
        port_map['subdomain'] = name
        if hostname:
            port_map['hostname'] = hostname
        self.tunnels = {'server1': port_map}

        self.yaml_path = os.path.join(
            self.runtime_dir,
            self.yaml_dirname,
            self.name + '.yml'
        )
        self.yaml_path_in_container = os.path.join(
            self.runtime_dir_in_container,
            self.yaml_dirname,
            self.name + '.yml'
        )

    def dumps(self):
        data = self.dump()
        yaml_str = yaml.dump(data, default_flow_style=False)
        return yaml_str

    def dump(self):
        data = {
            'server_addr': self.server_addr,
            'trust_host_root_certs': self.trust_host_root_certs,
            'tunnels': self.tunnels
        }
        return data

    def command(self):
        cmd = './release/ngrok -config /release/ngrok.conf'
        cmd = '.{0}/ngrok -log-level=INFO -log=stdout -config {1} start-all'.format(
            self.runtime_dir_in_container,
            self.yaml_path_in_container
        )
        return cmd

    def volumes(self):
        vs = [self.runtime_dir_in_container]
        binds = ['{0}:{1}:ro'.format(
            self.runtime_dir, self.runtime_dir_in_container)]
        return vs, binds

    def ports(self):
        # TODO
        ps = [9000]
        binds = ['{0}:{1}'.format(19000, 9000)]
        return ps, binds

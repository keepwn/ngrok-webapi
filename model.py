from peewee import *
import json
import string
import random

db = SqliteDatabase('data/database.db')


class Tunnel(Model):
    name = CharField(unique=True)  # subdomain
    hostname = CharField()
    localaddr = CharField()
    remoteport = CharField()
    proto = CharField()
    auth = CharField()
    starttime = IntegerField()

    class Meta:
        database = db


class Auth(Model):
    token = CharField()

    class Meta:
        database = db

    @staticmethod
    def token_gen(len):
        str = string.ascii_letters + string.digits
        keylist = [random.choice(str) for i in range(len)]
        return "".join(keylist)


def tunnel_to_dict(row):
    d = {}
    d['id'] = row.id
    d['name'] = row.name
    d['hostname'] = row.hostname
    d['localaddr'] = row.localaddr
    d['remoteport'] = row.remoteport
    d['proto'] = row.proto
    d['auth'] = row.auth
    d['starttime'] = row.starttime
    return d


def database_init():
    try:
        Tunnel.create_table()
    except OperationalError:
        print("tunnel table already exists!")
    try:
        Auth.create_table()
        random_token = Auth.token_gen(32)
        Auth.create(token=random_token)
        print("auth token: " + random_token)
    except OperationalError:
        print("auth table already exists!")


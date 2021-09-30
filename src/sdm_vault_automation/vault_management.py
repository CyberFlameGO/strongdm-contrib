import hvac
from . import consts
import os

import urllib3
urllib3.disable_warnings()

def get_path(path):
    read_response = get_client().secrets.kv.v1.read_secret(path=path)
    return read_response.get('data', None)

def put_path(path, secret):
    read_response = get_client().secrets.kv.v1.create_or_update_secret(path=path, secret=secret)
    return read_response

def get_client():
    vault_token = os.environ['VAULT_TOKEN'] if 'VAULT_TOKEN' in os.environ else None
    vault_addr = os.environ['VAULT_ADDR'] if 'VAULT_ADDR' in os.environ else None
    return hvac.Client(url=vault_addr, token=vault_token, verify=False)

def initialize_environ(vault_addr, vault_token):
    os.environ['VAULT_TOKEN'] = vault_token
    os.environ['VAULT_ADDR'] = vault_addr
    return is_initialized()

def is_initialized():
    if get_client().is_authenticated():
        return True
    return False

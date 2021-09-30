from . import vault_management as vault
from . import consts


def create_token(base_path, token_name, token, expiration):
    '''
    base_path: string
    tokename: string 
    token: string
    expiration: string
    write a secret to vault {"token":x, "expiration":z} 
    '''

    path = consts.TOKEN_PATH.format(**{'base_path':base_path, 'token_name':token_name})
    secret = consts.create_token_secret(token, expiration)
    return vault.put_path(path, secret)


def create_api(base_path, apiname, access_key, access_secret_key,  expiration):
    '''
    base_path: string
    apiname: string 
    access_key: string
    access_secret_key: string
    expiration: string
    write a secret to vault {"access_key":x, "access_secret_key":y, "expiration":z} 
    '''

    path = consts.API_PATH.format(**{'base_path':base_path, 'apiname':apiname})
    secret = consts.create_api_secret(access_key, access_secret_key, expiration)
    return vault.put_path(path, secret)


def read_token(base_path, token_name):
    path = consts.TOKEN_PATH.format(**{'base_path':base_path, 'token_name':token_name})
    return vault.get_path(path)
    
def read_fleet_token(base_path, token_name):
    path = consts.FLEET_TOKEN_PATH.format(**{'base_path':base_path, 'token_name':token_name})
    return vault.get_path(path)

def read_api(base_path, apiname):
    path = consts.API_PATH.format(**{'base_path':base_path, 'apiname':apiname})
    return vault.get_path(path)
    

def create_gateway_token(base_path, gatewayname, token):
    '''
    base_path: string
    relayname: string
    write a secret to vault SDM_RELAY_TOKEN: token
    '''
    path = consts.PROJECT_GATEWAY_PATH.format(**{'base_path':base_path, 
                                   'gatewayname':gatewayname})
    secret = {'SDM_RELAY_TOKEN': token}
    return vault.put_path(path, secret)


def read_gateway_token(base_path, gatewayname):
    '''
    base_path: string
    relayname: string
    read a secret from vault SDM_RELAY_TOKEN: token
    '''
    path = consts.PROJECT_GATEWAY_PATH.format(**{'base_path':base_path, 
                                   'gatewayname':gatewayname})
    return vault.get_path(path)
    

def create_relay_token(base_path, relayname, token):
    '''
    base_path: string
    relayname: string
    token: string
    write a relay secret from vault SDM_RELAY_TOKEN: token
    '''
    path = consts.PROJECT_RELAY_PATH.format(**{'base_path':base_path, 
                                   'relayname':relayname})
    secret = {'SDM_RELAY_TOKEN': token}
    return vault.put_path(path, secret)


def read_relay_token(base_path, relayname):
    '''
    base_path: string
    relayname: string
    read a relay secret from vault
    '''
    path = consts.PROJECT_RELAY_PATH.format(**{'base_path':base_path, 
                                   'relayname':relayname})
    return vault.get_path(path)

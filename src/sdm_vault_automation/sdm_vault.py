import os
from . import strongdm_management as sdm
from . import vault_management as vault
from . import vault_management_internal as vault_internal

from . import consts


def create_gateway(gatewayname, hostname, tags, vault_basepath):
    '''
    name 
    '''
    sdm_result = sdm.create_gateway(gatewayname, hostname, tags=tags)
    gateway_token = sdm_result.get('token')
    result = vault_internal.create_gateway_token(vault_basepath, gatewayname, gateway_token)
    return True


def create_relay(relayname, tags, vault_basepath):
    '''
    name 
    '''
    sdm_result = sdm.create_relay(relayname, tags=tags)
    gateway_token = sdm_result.get('token')
    result = vault_internal.create_relay_token(vault_basepath, relayname, gateway_token)
    return True


def create_account_attachments(rolename, user_emails=[], tags=None):
    tags = tags if not tags is None else {}
    valid_accounts = sdm.get_accounts_by_emails(user_emails)
    valid_emails = set([i.email for i in valid_accounts])

    # create the access rules for account
    aas_results = sdm.add_user_access(rolename, user_emails=valid_emails)
    return aas_results

def create_role_with_access(rolename, server_names, user_emails, tags={}):
    role = sdm.create_role(rolename, tags=tags)
    aas_results = create_account_attachments(rolename, user_emails)
    ras_results = sdm.add_resource_access(rolename, server_names)
    return role, aas_results, ras_results


def initialize_strongdm_from_vault(base_path, apiname):
    result = vault_internal.read_api(base_path, apiname)
    os.environ['SDM_API_SECRET_KEY'] = result.get('SDM_API_SECRET_KEY')
    os.environ['SDM_API_ACCESS_KEY'] = result.get('SDM_API_ACCESS_KEY')
    return True

def initialize_strongdm_token_from_vault(base_path, tokenname):
    result = vault_internal.read_token(base_path, tokenname)
    os.environ['SDM_ADMIN_TOKEN'] = result.get('SDM_ADMIN_TOKEN')
    return True

def initialize_strongdm_fleet_from_vault(base_path, tokenname):
    result = vault_internal.read_fleet_token(base_path, tokenname)
    os.environ['FLEET_ENROLLMENT_TOKEN'] = result.get('FLEET_ENROLLMENT_TOKEN')
    os.environ['FLEET_URL'] = result.get('FLEET_URL')
    return True



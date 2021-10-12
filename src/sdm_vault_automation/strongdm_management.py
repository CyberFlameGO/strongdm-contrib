import hvac
# from .consts import *
import os
import strongdm
import json

'''
See: https://github.com/strongdm/strongdm-sdk-python/blob/master/strongdm/models.py 

for building relevant objects
'''


def format_vault_string(vault_path, keyname):
    return '{}?key={}'.format(vault_path, keyname)


def get_listen_address(hostname, port):
    return "{}:{}".format(hostname, port)


def get_client():
    sdm_access = os.environ['SDM_API_ACCESS_KEY'] if 'SDM_API_ACCESS_KEY' in os.environ else None
    sdm_access_secret = os.environ['SDM_API_SECRET_KEY'] if 'SDM_API_SECRET_KEY' in os.environ else None
    return strongdm.Client(sdm_access, sdm_access_secret)


def get_role_by_name(name):
    '''
    get first object by name
    '''
    roles = [i for i in get_client().roles.list('name:{}'.format(name))]
    for i in roles:
        if i.name == name:
            return i
    return None


def get_roles(name):
    '''
    get first object by name
    '''
    roles = [i for i in get_client().roles.list('')]
    return roles


def get_resources(name):
    '''
    get first object by name
    '''
    roles = [i for i in get_client().resources.list('')]
    return roles


def get_roles_by_tags(tags: dict):
    '''
    get first object by name
    '''
    tag_str = ''
    if len(tags) > 0:
        tag_str = ','.join(['{}:{}'.format(k, v) for k, v in tags.items()])
    results = [i for i in get_client().roles.list(tag_str)]
    return results


def get_resource_by_name(name):
    '''
    get first object by name
    '''
    roles = [i for i in get_client().resources.list('name:{}'.format(name))]
    for i in roles:
        if i.name == name:
            return i
    return None


def get_resources_by_names(names):
    '''
    get first object by name
    '''
    roles = [i for i in get_client().resources.list('')]
    results = []
    for i in roles:
        if i.name in names:
            results.append(i)
    return results


def get_resources_by_tags(tags: dict):
    '''
    resources by tags
    '''
    tag_str = ''
    if len(tags) > 0:
        tag_str = ','.join(['{}:{}'.format(k, v) for k, v in tags.items()])
    results = [i for i in get_client().resources.list(tag_str)]
    return results


def get_account_by_email(email):
    '''
    get first object by name
    '''
    roles = [i for i in get_client().accounts.list('email:{}'.format(email))]
    for i in roles:
        if i.email == email:
            return i
    return None


def get_accounts_by_emails(emails):
    '''
    get first object by name
    '''
    roles = [i for i in get_client().accounts.list('')]
    accounts = []
    for i in roles:
        if i.email in emails:
            accounts.append(i)
    return accounts


def get_accountattachment(role_id, account_id):
    '''
    get first object by name
    '''
    aas = [i for i in get_client().account_attachments.list(
        'account_id:{},role_id:{}'.format(account_id, role_id))]
    for i in aas:
        if i.account_id == account_id and i.role_id == role_id:
            return i
    return None


def get_node_by_name(name):
    '''
    get first object by name
    '''
    roles = [i for i in get_client().nodes.list('name:{}'.format(name))]
    for i in roles:
        if i.name == name:
            return i
    return None


def get_secretstore_by_name(name):
    roles = [i for i in get_client().secret_stores.list('name:{}'.format(name))]
    for i in roles:
        if i.name == name:
            return i
    return None


def create_vault_secretstore(name, server_address, tags={}):
    role = get_secretstore_by_name(name)
    if role is not None:
        raise Exception("SecretStore {} exists".format(name))

    tags = {} if tags is None else tags

    example = {'id': None,
               'name': name,
               'server_address': server_address,
               'tags': tags
               }
    vss = strongdm.models.VaultTokenStore(**example)
    return get_client().secret_stores.create(vss).to_dict()


def create_role(name, tags=None, access_rules='', composite=False):
    role = get_role_by_name(name)
    if role is not None:
        raise Exception("Role {} exists".format(name))

    tags = {} if tags is None else tags
    example = {'id': None, 'name': name,
               'access_rules': access_rules,
               'composite': composite, 'tags': tags}
    role = strongdm.models.Role(**example)
    return get_client().roles.create(role).to_dict()


def create_ssh_server(name, hostname, username, privatekey, port, tags=None,
                      egress_filter='', port_forwarding=False, allow_deprecated_key_exchanges=False,
                      secretstore_id=None, secretstore_name=None):

    if secretstore_id is None and not secretstore_name is None:
        secretstore = get_secretstore_by_name(secretstore_name)
        secretstore_id = secretstore.id

    server = get_resource_by_name(name)
    if server is not None:
        raise Exception("Server {} exists".format(name))

    tags = {} if tags is None else tags

    example = {'id': None, 'name': name, 'tags': tags,
               'hostname': hostname, 'egress_filter': egress_filter,
               'username': username, 'private_key': privatekey,
               'port': port, 'port_forwarding': port_forwarding,
               'allow_deprecated_key_exchanges': allow_deprecated_key_exchanges,
               'secret_store_id': secretstore_id}
    server = strongdm.models.SSHCustomerKey(**example)
    return get_client().resources.create(server).to_dict()


def create_ssh_server_vault(name, hostname, vault_path, username_key, privatekey_key, port, tags=None,
                            egress_filter='', port_forwarding=False, allow_deprecated_key_exchanges=False,
                            secretstore_name=None, secretstore_id=None):

    if secretstore_id is None:
        secretstore_id = get_secretstore_by_name(secretstore_name)

    if secretstore_id is None:
        raise Exception("no secret store exists")

    username = format_vault_string(vault_path, username_key)
    privatekey = format_vault_string(vault_path, privatekey_key)
    return create_ssh_server(name, hostname, username, privatekey,
                             port, tags, egress_filter, port_forwarding,
                             allow_deprecated_key_exchanges, secret_store_id=secretstore_id).to_dict()


def delete_resource_by_name(name):
    '''
    delete resource nodes by name
    '''
    nodes = [i for i in get_client().resources.list('name:{}'.format(name))]
    return [get_client().resources.delete(i.id) for i in nodes]


def delete_resource_by_hostname(name):
    '''
    delete resources by hostname
    '''
    nodes = [i for i in get_client().resources.list(
        'hostname:{}'.format(name))]
    return [get_client().resources.delete(i.id) for i in nodes]


# def delete_resource_by_username(name):
#     '''
#     delete resources by username, note if its a vault path, that needs to be provided
#     '''
#     nodes = [i for i in get_client().resources.list('') if getattr(i, 'username', '') == name]
#     return [get_client().resources.delete(i.id) for i in nodes]


def create_account(first_name, last_name, email, tags=None, suspended=False):
    account = get_account_by_email(email)
    if account is not None:
        raise Exception("Account {} exists".format(email))

    tags = {} if tags is None else tags

    example = {'id': None, 'email': email, 'first_name': first_name,
               'last_name': last_name, 'suspended': suspended, 'tags': tags}
    user = strongdm.models.User(**example)
    return get_client().accounts.create(user).to_dict()


def delete_user_by_email(email):
    '''
    delete relay nodes by name
    '''
    nodes = [i for i in get_client().accounts.list('email:{}'.format(email))]
    return [get_client().accounts.delete(i.id) for i in nodes]


def delete_role_by_name(name):
    '''
    delete relay nodes by name
    '''
    nodes = [i for i in get_client().roles.list('name:{}'.format(name))]
    return [get_client().roles.delete(i.id) for i in nodes]


def create_gateway(name, hostname, port=5000, bindaddress='0.0.0.0', tags=None, gateway_filter=''):
    '''
    returns raw response dict:
        `token` is what will be used by the SDM agent to auth with the control plane
        `node` is the SDM model object
    '''

    gateway = None if name is None else get_node_by_name(name)
    if gateway is not None:
        raise Exception("Gateway {} exists".format(name))

    tags = {} if tags is None else tags
    example = {
        'name': name,
        'listen_address': get_listen_address(hostname, port),
        'state': None,
        'bind_address': get_listen_address(bindaddress, port),
        'gateway_filter': gateway_filter,
        'tags': tags,
    }
    gateway = strongdm.models.Gateway(**example)
    return get_client().nodes.create(gateway).to_dict()


def create_relay(name, tags=None, gateway_filter=''):
    '''
    returns raw response dict:
        `token` is what will be used by the SDM agent to auth with the control plane
        `node` is the SDM model object
    '''
    relay = None if name is None else get_node_by_name(name)
    if relay is not None:
        raise Exception("Relay {} exists".format(name))

    tags = {} if tags is None else tags
    example = {
        'name': name,
        'state': None,
        'tags': tags,
        'gateway_filter': gateway_filter
    }
    relay = strongdm.models.Relay(**example)
    return get_client().nodes.create(relay).to_dict()


def delete_nodes_by_name(name):
    '''
    delete relay nodes by name
    '''
    nodes = [i.name == name for i in get_client(
    ).nodes.list('name:{}'.format(name))]
    return [get_client().nodes.delete(i).to_dict() for i in nodes]


def delete_nodes_by_hostname(hostname):
    '''
    delete relay nodes by name
    '''
    # relay nodes do not have a hostname, so we use indirect access
    nodes = [i for i in get_client().nodes.list(
        'hostname:{}'.format(hostname))]
    return [get_client().nodes.delete(i).to_dict() for i in nodes]


def add_resource_access(rolename, resource_names=[]):
    '''
    rolename: string
    resource_names: [string] list of resource names

    '''
    roles = [i for i in get_client().roles.list('name:{}'.format(rolename))]
    if len(roles) == 0:
        raise Exception("Rolename not found: {}".format(rolename))
    role = roles[0]
    nodes = []
    for name in resource_names:
        nodes = nodes + \
            [i for i in get_client().resources.list('name:{}'.format(name))]

    # nodes = [i for i in get_client().resources.list('') if i.name in resource_names]
    access_rules = json.dumps([{"ids": [i.id for i in nodes]}])
    setattr(role, 'access_rules', access_rules)
    return get_client().roles.update(role)


def remove_resource_access(rolename, resource_names=[]):
    '''
    rolename: string
    resource_names: [string] list of resource names

    '''
    roles = [i for i in get_client().roles.list('name:{}'.format(rolename))]
    if len(roles) == 0:
        raise Exception("Rolename not found: {}".format(rolename))
    role = roles[0]

    nodes = [i for i in get_client().resources.list('')
             if i.name in resource_names]
    drop_ids = set([i.id for i in nodes if i.name])
    old_access_rules = json.loads(role.access_rules)[0].get('ids', [])
    new_ids = [i for i in old_access_rules if not i in drop_ids]
    new_access_rules = None
    if len(new_ids) > 0:
        new_access_rules = json.dumps([{"ids": new_ids}])
    setattr(role, 'access_rules', new_access_rules)
    return get_client().roles.update(role)


def create_account_attachment_by_id(role_id, account_id):
    aa = get_accountattachment(role_id, account_id)
    if not aa is None:
        return Exception("AccountAttachment exists for role_id: {} and account_id: {}".format(role_id, account_id))

    example = {
        'account_id': account_id,
        'role_id': role_id,
    }
    aa = strongdm.models.AccountAttachment(**example)
    return get_client().account_attachments.create(aa)


def create_account_attachment_by_names(rolename, user_email):
    roles = [i for i in get_client().roles.list('name:{}'.format(rolename))]
    if len(roles) == 0:
        raise Exception("Rolename not found: {}".format(rolename))

    users = [i for i in get_client().accounts.list(
        'email:{}'.format(user_email))]
    if len(users) == 0:
        raise Exception("User email not found: {}".format(user_email))

    user = users[0]
    role = roles[0]
    return create_account_attachment_by_id(role.id, user.id)


def add_user_access(rolename, user_emails=[]):
    '''
    rolename: string
    resource_names: [string] list of resource names

    '''
    roles = [i for i in get_client().roles.list('name:{}'.format(rolename))]
    if len(roles) == 0:
        raise Exception("Rolename not found: {}".format(rolename))
    role = roles[0]
    role_id = role.id
    users = []
    for email in user_emails:
        users = users + \
            [i for i in get_client().accounts.list('email:{}'.format(email))]

    results = []
    aas = []
    for user in users:
        i = get_client().account_attachments.list(
            'account_id:{},role_id:{}'.format(user.id, role.id))
        aas = aas + [x for x in i]

    aas_valid = {"{}:{}".format(aa.role_id, aa.account_id): aa for aa in aas}
    for user in users:
        key = "{}:{}".format(role_id, user.id)
        aa = aas_valid.get(key, None)
        if aa is not None:
            continue
        results.append(create_account_attachment_by_id(role.id, user.id))
    return results


def remove_user_access(rolename, user_emails=[]):
    '''
    rolename: string
    resource_names: [string] list of resource names

    '''
    roles = [i for i in get_client().roles.list('name:{}'.format(rolename))]
    if len(roles) == 0:
        raise Exception("Rolename not found: {}".format(rolename))
    role = roles[0]
    role_id = role.id

    users = []
    for email in user_emails:
        users = users + \
            [i for i in get_client().accounts.list('email:{}'.format(email))]

    aas = []
    for user in users:
        aas = aas + [i for i in get_client().account_attachments.list(
            'account_id:{},role_id:{}'.format(user.id, role.id))]

    # aas = [i for i in get_client().account_attachments.list('')]
    aas_valid = {"{}:{}".format(aa.role_id, aa.account_id): aa for aa in aas}

    results = []
    for user in users:
        key = "{}:{}".format(role_id, user.id)
        aa = aas_valid.get(key, None)
        if aa is not None:
            r = get_client().account_attachments.delete(aa.id)
            results.append(r)
    return results


def assign_new_secret_store(old_secret_store, new_secret_store, server_names=[]):
    '''
    rolename: string
    resource_names: [string] list of resource names

    '''
    old_ss = get_secretstore_by_name(old_secret_store)
    new_ss = get_secretstore_by_name(new_secret_store)

    servers = []
    if len(server_names) == 0:
        # assign all servers
        servers = [i for i in get_client().resources.list(
            'secret_store_id:{}'.format(old_ss.secret_store_id))]

    for server in servers:
        server.secret_store_id = new_ss.id
        get_client().resources.update(server)

    return servers

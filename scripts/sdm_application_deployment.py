import json
import os
import strongdm
from sdm_vault_automation import vault_management as vault
from sdm_vault_automation import strongdm_management as sdm
from sdm_vault_automation import sdm_vault

import argparse
import urllib3
urllib3.disable_warnings()

VAULT_TOKEN = os.environ.get('VAULT_TOKEN', None)
VAULT_ADDR = os.environ.get('VAULT_ADDR', None)

parser = argparse.ArgumentParser(description='Create StrongDM Setup.')
parser.add_argument('-vault_addr', type=str, default=VAULT_ADDR, help='set vault_addr')
parser.add_argument('-vault_token', type=str, default=VAULT_TOKEN, help='set vault_token')
parser.add_argument('-vault_bpath', type=str, default=None, help='set vault base path')

parser.add_argument('-sdm_apiname', type=str, default=None, help='set strongdm API keys from vault')

parser.add_argument('-create_gateways', type=str, default=None, help='create gatway: [{"hostname":"127.0.0.1", "name":"testy_testy"}]')
parser.add_argument('-create_relays', type=str, default=None, help='create relays: [{"name":"testy_testy"}]')

parser.add_argument('-create_roles', type=str, default=None, help='create gatway: [{"name":"testy-role",}')
parser.add_argument('-create_users', type=str, default=None, help='create gatway: [{"name":"testy-role",}]')
parser.add_argument('-create_ssh_servers', type=str, default=None, help='create ssh server: {"name":"testy-role",}')
parser.add_argument('-create_vault_stores', type=str, default=None, help='create vault secrets: [{"name":"testy-role","address":"https://testy_testy:8200"}]')

parser.add_argument('-delete_roles', type=str, default=None, help='delete roles: [{"name":"testy-role",}')
parser.add_argument('-delete_users', type=str, default=None, help='delete users by email: [{"name":"testy@example.com",}]')
parser.add_argument('-delete_resources', type=str, default=None, help='delete servers, etc.: {"name":"testy-role",}')

parser.add_argument('-attach_users', type=str, default=None, help='create role to user mapping: {"rolename":"testy-role", "user_emails": [test@test.com]}')
parser.add_argument('-attach_resources', type=str, default=None, help='create role to resource mapping: {"rolename":"testy-role", "user_emails": [test@test.com]}')

parser.add_argument('-detach_users', type=str, default=None, help='detach role to user mapping: {"rolename":"testy-role", "user_emails": [test@test.com]}')
parser.add_argument('-detach_resources', type=str, default=None, help='detach role to resource mapping: {"rolename":"testy-role", "servers": ["testy"]}')

parser.add_argument('-tags', type=str, default='{"source":"automation"}', help='tags to use')


'''
python3 strongdm_application_deployment.py -vault_bpath "teams/secret_infosec/apridgen/" -sdm_apiname "testing-api-key" \
            -vault_addr "https://vault.example.com:8200" -vault_token "s." \
            -attach_resources '[{"rolename":"testy_testy", "servers": ["testy_testy"]}]' \
            -create_ssh_servers '[{"name": "testy_testy", "hostname": "testy_testy", "username": "username_or_vp", "privatekey": "privatekey_or_vp", "port": 444, "secretstore_name":"testy_testy"}]' \
            -create_vault_stores '[{"name": "testy_testy", "address": "testy_testy"}]' \
            -create_roles '[{"name":"testy_testy"}]' \
            -create_users '[{"first_name":"Testy", "last_name":"Testy", "email": "testy@example.com"}]' \
            -attach_users '[{"rolename":"testy_testy", "user_emails": ["testy@example.com"]}]' \
            -create_gateways '[{"name":"testy_testy", "hostname":"127.0.0.1"}]'

python3 strongdm_application_deployment.py -vault_bpath "teams/secret_infosec/apridgen/" -sdm_apiname "testing-delete-key" \
            -vault_addr "https://vault.example.com:8200" -vault_token "s." \
            -delete_resources '[{"name": "testy_testy"}]' \
            -delete_roles '[{"name":"testy_testy"}]' \
            -delete_users '[{"email": "testy@example.com"}]'

python3 strongdm_application_deployment.py -vault_bpath "teams/secret_infosec/apridgen/" -sdm_apiname "testing-api-key" \
            -vault_addr "https://vault.example.com:8200" -vault_token "s." \
            -detach_resources '[{"rolename":"testy_testy", "servers": ["testy_testy"]}]' \
            -detach_users '[{"rolename":"testy_testy", "user_emails": ["testy@example.com"]}]'

'''


if __name__ == "__main__":
    args = parser.parse_args()

    base_path = args.vault_bpath
    #0. get the SDM API key from vault
    vault.initialize_environ(args.vault_addr, args.vault_token)
    sdm_vault.initialize_strongdm_from_vault(base_path, args.sdm_apiname)

    tags = json.loads(args.tags) if args.tags is not None else {}
    
    # 1. creating a gateways (1-2)
    # 2. saving gateway token to a vault path
    if args.create_gateways is not None:    
        infos = json.loads(args.create_gateways)
        for data in infos:
            gatewayname = data['name']
            hostname = data['hostname']
            print("Creating a gateway ({}) with name {}, storing the token in: {}".format(gatewayname, hostname, base_path))
            try:
                result = sdm_vault.create_gateway(gatewayname, hostname, tags, base_path)
            except:
                pass
            # results.append(x)
    if args.create_relays is not None:    
        infos = json.loads(args.create_relays)
        for data in infos:
            gatewayname = data['name']
            print("Creating a gateway ({}) with name {}, storing the token in: {}".format(gatewayname))
            try:
                result = sdm_vault.create_relay(gatewayname, tags, base_path)
            except:
                pass
            # results.append(x)

    # 2. create a user
    if args.create_roles is not None:
        roles = json.loads(args.create_roles)
        for data in roles:
            rolename = data['name']
            print("Creating a role: {}".format(rolename))
            result = sdm.create_role(rolename, tags)
            # results.append(x)

    # 3. create a user
    if args.create_users is not None:
        users = json.loads(args.create_users)
        results = []
        for data in users:
            first_name = data['first_name']
            last_name = data['last_name']
            email = data['email']
            print("Creating a user: {}".format(email))
            x = sdm.create_account(first_name, last_name, email)
            # results.append(x)

    # 4. attach users to a role
    if args.attach_users is not None:
        infos = json.loads(args.attach_users)
        for data in infos:
            rolename = data['rolename']
            user_emails = data['user_emails']
            print("Adding users to {}: {}".format(rolename, str(user_emails)))
            result = sdm_vault.create_account_attachments(rolename, user_emails)
            # print(result)

    if args.detach_users is not None:
        infos = json.loads(args.detach_users)
        for data in infos:
            rolename = data['rolename']
            user_emails = data['user_emails']
            print("Adding users to {}: {}".format(rolename, str(user_emails)))
            result = sdm.remove_user_access(rolename, user_emails)
            # print(result)

    # 5. create valut token secret store
    if args.create_vault_stores is not None:
        infos = json.loads(args.create_vault_stores)
        for data in infos:
            addr = data['address']
            name = data['name']
            print("Creating a Vault Secret Store using tokens {}: {}".format(name, addr))
            try:
                result = sdm.create_vault_secretstore(name, addr)
            except:
                pass
            # print(result)

    # 5. create a server
    #TODO
    if args.create_ssh_servers is not None:
        infos = json.loads(args.create_ssh_servers)
        for data in infos:
            name = data.get('name', None)
            hostname = data.get('hostname', None)
            username = data.get('username', None)
            privatekey = data.get('privatekey', None)
            port = data.get('port', None)
            secretstore_name = data.get('secretstore_name', None)
            print("Creating an SSH Server with {}: {}:{} {}".format(name, addr, port, username))
            result = sdm.create_ssh_server(name, hostname, username, privatekey, port, 
                tags=tags, secretstore_name=secretstore_name)
            # print(result)

    # 6. attach resources to a role
    #TODO
    if args.attach_resources is not None:
        infos = json.loads(args.attach_resources)
        for data in infos:
            rolename = data['rolename']
            servers = data['servers']
            print("Attaching servers to {}: {}".format(rolename, str(servers)))
            result = sdm.add_resource_access(rolename, servers)
            # print(result)

    if args.detach_resources is not None:
        infos = json.loads(args.detach_resources)
        for data in infos:
            rolename = data['rolename']
            servers = data['servers']
            print("Detaching resources to {}: {}".format(rolename, str(servers)))
            result = sdm.remove_resource_access(rolename, servers)
            # print(result)

    # 7. delete resources
    if args.delete_resources is not None:
        infos = json.loads(args.delete_resources)
        for data in infos:
            name = data.get('name', None)
            print("Deleting server to {}".format(name))
            result = sdm.delete_resource_by_name(name)
            # print(result)

    # 8. delete users
    if args.delete_users is not None:
        infos = json.loads(args.delete_users)
        for data in infos:
            name = data.get('email', None)
            print("Deleting user to {}".format(name))
            result = sdm.delete_user_by_email(name)
            # print(result)

    # 8. delete users
    if args.delete_roles is not None:
        infos = json.loads(args.delete_roles)
        for data in infos:
            name = data.get('name', None)
            print("Deleting Role to {}".format(name))
            try:
                result = sdm.delete_role_by_name(name)
                print(result)
            except:
                pass



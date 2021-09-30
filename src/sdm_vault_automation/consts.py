# handle user operations
USER_TOKEN_PATH = "{base_path}/strongdm/users/{username}/tokens/{token_name}/".replace('//', '/')
USER_TOKEN_SECRET = {"value":None, "expiration":None}

USER_API_PATH = "{base_path}/strongdm/users/{username}/apis/{apiname}/".replace('//', '/')
USER_API_SECRET = {"access_key":None, "access_secret_key":None, "expiration":None}

# handle user operations
TOKEN_PATH = "{base_path}/strongdm/tokens/{token_name}/".replace('//', '/')
TOKEN_SECRET = {"SDM_ADMIN_TOKEN":None, "expiration":None}

# handle user operations
FLEET_TOKEN_PATH = "{base_path}/strongdm/fleet_tokens/{token_name}/".replace('//', '/')
FLEET_TOKEN_SECRET = {"FLEET_ENROLLMENT_TOKEN":None, "FLEET_URL":None, "expiration":None}

API_PATH = "{base_path}/strongdm/apis/{apiname}/".replace('//', '/')
API_SECRET = {"access_key":None, "access_secret_key":None, "expiration":None}

create_token_secret = lambda value, expiration: {'value': value, 'expiration': expiration}
create_api_secret =lambda x, y, z: {"SDM_API_ACCESS_KEY":x, "SDM_API_SECRET_KEY":y, "expiration":z}



PROJECT_GATEWAY_PATH = "{base_path}/strongdm/gateways/{gatewayname}".replace('//', '/')
PROJECT_RELAY_PATH = "{base_path}/strongdm/relays/{relayname}".replace('//', '/')

# accounts 
PROJECT_SERVER_PATH = "{base_path}/strongdm/servers/{servername}".replace('//', '/')
PROJECT_DATASOURCES_PATH = "{base_path}/strongdm/datasources/{accountname}".replace('//', '/')
PROJECT_WEBSITES_PATH = "{base_path}/strongdm/websites/{accountname}".replace('//', '/')
PROJECT_CLUSTERS_PATH = "{base_path}/strongdm/clusters/{accountname}".replace('//', '/')

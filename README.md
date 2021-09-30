## Overview

This repository is used to show how to use StrongDM in a Nomad environment.  The project includes sample Nomad Jobs specifications and a sample Python utility for automation.


## Nomad Notes
Apart from resources (e.g. clusters, datasources, servers) StrongDM is composed primarily of _gateways_ and _relays_.  The StrongDM documentation provided details for deploying these components in AWS, GCP, etc., but there was no documentation supporting HashiCorp Nomad + Vault.

These notes highlight some of the pre-requisites for deploying _gateways_ and _relays_ to Nomad.  See [strongdm-gateway-example.nomad](https://github.com/Roblox/strongdm-contrib/blob/main/nomad-jobs/strongdm-gateway-example.nomad) for specific. 

### **DNS Name for Reachability**

A DNS CNAME, DNS A-record or direct IP address is necessary for clients to reach the _gateways_.  ITO or the team that performs common infrastructure setup needs to set-up the records.  

**Note:** The gateway only needs to be reachable by the client, so it can go on a private network that accessible only to the client.

### **Using Vault with StrongDM**

Vault set-up is straight forward.  This service is required for two reasons:
1. Obtain the _relay_ token used to authenticate the component to the control plane
2. Set a `VAULT` token that allows the **gateway** or **relay** to authenticate to the Vault Service for resource secrets.  This configuration means usernames and passwords can be stored and read from a Vault path.  

#### **Configuring Nomad Job to use Vault**

In the `job` stanza, simply include a block for the `vault` configuration.  The `env` value must be set to `true`, and the relevant policies must be specified:
```
vault {
    policies      = ["YOUR_POLICY"]
    env           = true
    change_mode   = "signal"
    change_signal = "SIGHUP"
  }
```

#### **Configuring Nomad to Read StrongDM Token from Vault**
The `SDM_RELAY_TOKEN` is a required environment variable for the StrongDM container.  The `task` stanza must include a `template` block that specifies where to read the token from in Vault.  Below the path to the target token is stored in, `secret/path/to/strongdm/gateways/strongdm_gw_00_simulpong`.  **Note** to simplify the access patterns, `strongdm/gateways/NAME` the KV store is organized in the following heirarchy: `application` -> `gateways` -> `gateway NAME`. 

```
      template {

        data = <<EOD
SDM_RELAY_TOKEN={{ with secret "secret/path/to/strongdm/gateways/strongdm_gw_00_simulpong" }}{{ .Data.SDM_RELAY_TOKEN}}{{ end}}
EOD

        destination = "secrets/file.env"
        env         = true
      }
```

### **Other considerations**

**Gateways** must have a port exposed.  The default port is **5000**, but it can be adjusted in the `job` specification and in the control plane GUI or API.  Below is a sample `network` block found in the `job` stanza.  Note, **relays** do not require any inbound network connectivity.  They will connect to **gateways** based on configuration information they receive from the control plane.  

```
    network {
      mode = "bridge"

      port "strongdm_proxy" {
        static = "5000"
        to     = "5000"
      }
    }
```

## Basic Python Automation Framework

StrongDM includes a robust API to help automate the creation of components, users and roles.  This helps us rapidly scale-up or scale-down StrongDM infrastructure, and then as teams or infrastructure expand and contract, we can provision or deprovision users and resources.  The repository contains a barebone framework that helps demonstrate how the automation might work.

It's assumed that `teams/path_to_strongdm/`.  If this base path is supplied and the StrongDM API key `testing-api-key` is to be accessed, the tool will look in `teams/path_to_strongdm/apis/testng-api-key` for the `SDM_API_SECRET_KEY` and `SDM_API_ACCESs_KEY`. 

### **Setting up the Python Environmet**

0. Add StrongDM API Keys to Vault, _assuming_ `teams/path_to_strongdm/` is the base Vault Path to relevant secrets
1. Clone this repository
2. Create the Python3 Virtual Environment and activate it
3. Install the prerequisites
4. Install the tooling
5. Log into Vault and get a token
6. Easily manage the StrongDM
   1. configure the _roles_, _users_, a subset of _resources_
   2. create a _Vault Secret Store_, _relays_, and _gateways_

### **Running the Tools**

#### **Creating Relevant Components and Attaching Policies**

```
python3 sdm_application_deployment.py -vault_bpath "teams/path/to/strongdm" -sdm_apiname "testing-api-key" \
            -vault_addr "https://vault.localhost.com:8200" -vault_token "s.YOURTOKEN" \
            -attach_resources '[{"rolename":"testy_testy", "servers": ["testy_testy"]}]' \
            -create_ssh_servers '[{"name": "testy_testy", "hostname": "testy_testy", "username": "username_or_vp", "privatekey": "privatekey_or_vp", "port": 444, "secretstore_name":"testy_testy"}]' \
            -create_vault_stores '[{"name": "testy_testy", "address": "testy_testy"}]' \
            -create_roles '[{"name":"testy_testy"}]' \
            -create_users '[{"first_name":"Testy", "last_name":"Testy", "email": "testy@example.com"}]' \
            -attach_users '[{"rolename":"testy_testy", "user_emails": ["testy@example.com"]}]' \
            -create_gateways '[{"name":"testy_testy", "hostname":"127.0.0.1"}]'
```

##### **What happens:**
This command performs several activities:
1. Create a new *vault secret store* component for accessing secrets stored in Vault
2. Create _roles_ used to manage _user_ access to _resources_
3. Create _gateway_ (or _relays_) and stores the token in Vault using the `vault_bpath`.
4. Create _resources_ that use a specific secret store with specific paths to the credentials in Vault.
5. Create new _users_ 
6. Attach _users_ to a specific _role_ 
7. Attach _resources_ to a specific _role_, granting users in this _role_ access to the resources 

The framework uses the Vault token to initialize the SDM environment variables, and for each command:
1. the framework checks the creation of each new component to determine if they are already exist.  If they do not exist, the action continues. 
2. Before attaching components to a _role_, the framework resolves the _server_ or _user_ component's ID if they exist and creates the relevant association.  In the case of a _user_, an `AccountAttachment` is created, and for resources, new _access rules_ are created and added to the _role_.
3. When _gateways_ or _relays_ are created, the new token is stored in Vault for subsequent access.

#### **Detaching Accsses Policies**
##### **Example Command:**
```
python3 sdm_application_deployment.py -vault_bpath "teams/path/to/strongdm" -sdm_apiname "testing-api-key" \
            -vault_addr "https://vault.localhost.com:8200" -vault_token "s.YOURTOKEN" \
            -detach_resources '[{"rolename":"testy_testy", "servers": ["testy_testy"]}]' \
            -detach_users '[{"rolename":"testy_testy", "user_emails": ["testy@example.com"]}]'

```
##### **What happens:**
This command performs several activities:
1. Update resource access rules and remove the servers from the specified role.  These servers will no longer be accessible from this particular role, and all user's sessions will be terminated.
2. Update resource access rules and remove the users from the specified role.  All usrs will be removed from the role, and they will no longer have access to resources in this role.

The framework uses the Vault token to initialize the SDM environment variables, and for each command:
1. the framework resolves the _role_ component's ID
2. the framework resolves the _server_ or _user_ component's ID
3. In the case of the _user_, the `AccountAttachment` with the relevant `role.id` is identified and **deleted**
3. In the case of the _resources_, the `role.access_rules` are updated by removing the `ids` that correspond to the _resources_. 


#### **Deleting Components**

##### **Example Command:**
```
python3 sdm_application_deployment.py -vault_bpath "teams/path/to/strongdm" -sdm_apiname "testing-delete-key" \
            -vault_addr "https://vault.localhost.com:8200" -vault_token "s.YOURTOKEN" \
            -delete_resources '[{"name": "testy_testy"}]' \
            -delete_roles '[{"name":"testy_testy"}]' \
            -delete_users '[{"email": "testy@example.com"}]'
```

##### **What happens:**
First notice, a separate key (e.g. **`testing-delete-key`**) is used to delete resources for safety.  

This command performs several activities:
1. Delete all resources with the name of `testy_testy`
2. Delete all roles with the name of `testy_testy`
3. Delete all roles with the name of `testy@example.com`

The framework uses the Vault token to initialize the SDM environment variables, and for each command:
1. the framework resolves the _role_ component's by name and then deletes them
2. the framework resolves the _user_ component's by name and then deletes them
3. the framework resolves the _resource_ component's by name and then deletes them


## Docker Image

### Overview

The docker container runs a service that reads audit logs from StrongDM and forwards them to our ES SIEM, and it depends on:
1. ElastiSearch's Fleet Agent
2. StrongDM Linux Client 
3. Python3 which is the base Docker image

This dockerfile is used to create a log connector between StrongDM and ElastiSearch
At a minimum the container will require environment variables for:
1. **`VAULT_TOKEN`**: passed in via Nomad
2. **`VAULT_ADDRESS`**: set in Nomad Job Spec
3. **`VAULT_BPATH`**: set in Nomad Job Spec, base path for all the SDM Secrets

Other Accepted environment variables:
1. **`SDM_ADMIN_TOKEN_NAME`**: admin token name for the token  found using valut base path, default: `sdm_audit_admin`
2. **`AUDIT_START`**: time to start from when reading logs, if nothing is specified current UTC time is used isoformat `YYYY-MM-DDTHH:MM:SS.000000Z`
3. **`DEFAULT_SLEEP`**: how long to sleep for between log checks, default: `60.0`
4. **`DEFAULT_OUTPUT`**: place where to write logs in the docker container, default: `/opt/logs/strongdm.json`
5. **`FLEET_TOKEN_NAME`**: token name for the fleet token name for the token  found using valut base path, default: `fleet`


The `sdm_audit_svc.py` will populate the following environment variables by reading out variables from Vault:
1. **`SDM_ADMIN_TOKEN`:** `{base_path}/strongdm/tokens/{token_name} token_name is a parameter to the command, default: sdm_audit_admin`
2. **`FLEET_ENROLLMENT_TOKEN`:** `{base_path}/strongdm/fleet_tokens/{token_name} token_name is a parameter to the command, default: fleet`
3. **`FLEET_URL`:** `{base_path}/strongdm/fleet_tokens/{token_name} token_name is a parameter to the command, default: fleet`


**Build Command (from root project dir)**: 
```
docker build --no-cache -t sdm-collector:latest \
--build-arg SSH_PRV_KEY="$SSH_PRV_KEY" - < ./docker/sdm_audit.Dockerfile
```

**Docker Run Prep and Execution**:
```
sudo docker run -d -t \
-e VAULT_ADDRESS=$VAULT_ADDRESS \
-e VAULT_TOKEN=$VAULT_TOKEN \
-e VAULT_BPATH=$VAULT_BPATH \
-e SDM_ADMIN_TOKEN_NAME="sdm_audit_admin" \
-e FLEET_TOKEN_NAME="fleet" \
-e AUDIT_START=2021-09-01T00:00:00.000000Z \
--name sdm-collector sdm-collector:latest python3 sdm_log_svc.py
```



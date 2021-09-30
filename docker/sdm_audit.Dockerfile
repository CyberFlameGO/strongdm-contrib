# docker build  -t sdm-collector:latest --build-arg SSH_PRV_KEY="$SSH_PRV_KEY" - < ./sdm_audit.Dockerfile
# This dockerfile is used to create a log connector between StrongDM and ElastiSearch
# At a minimum the container will require environment variables for:
# 1. VAULT_TOKEN: passed in via Nomad
# 2. VAULT_ADDRESS: set in Nomad Job Spec
# 3. VAULT_BPATH: set in Nomad Job Spec, base path for all the SDM Secrets

# Other Accepted environment variables:
# 1. SDM_ADMIN_TOKEN_NAME: admin token name for the token  found using valut base path 
# 2. AUDIT_START: time to start from when reading logs, if nothing is specified current UTC time is used, isoformat YYYY-MM-DDTHH:MM:SS.000000Z
# 3. DEFAULT_SLEEP: how long to sleep for between log checks
# 4. DEFAULT_OUTPUT: place where to write logs in the docker container
# 5. FLEET_TOKEN_NAME: token name for the fleet token name for the token  found using valut base path


# The sdm_audit_svc.py will populate the following environment variables by reading out variables from Vault:
# SDM_ADMIN_TOKEN: {base_path}/strongdm/tokens/{token_name} token_name is a parameter to the command, default: sdm_audit_admin
# FLEET_ENROLLMENT_TOKEN: {base_path}/strongdm/fleet_tokens/{token_name} token_name is a parameter to the command, default: fleet
# FLEET_URL: {base_path}/strongdm/fleet_tokens/{token_name} token_name is a parameter to the command, default: fleet
FROM python:3
RUN apt update && apt -y install unzip

WORKDIR /opt/

# https://www.elastic.co/guide/en/fleet/current/elastic-agent-installation.htmlDEFAULT_PATH_ELASTIC_AGENT
# Note: there sdm_audit_svc.py expects the elastic-agent-linux to be here: /opt/elastic-agent-linux/, dont change this 
RUN curl -L -O https://artifacts.elastic.co/downloads/beats/elastic-agent/elastic-agent-7.15.0-linux-x86_64.tar.gz && \
    tar xzvf elastic-agent-7.15.0-linux-x86_64.tar.gz && \
    mv elastic-agent-7.15.0-linux-x86_64 elastic-agent-linux && \
    mkdir -p /opt/logs/ && touch /opt/logs/strongdm.json && \
    mkdir -p ~/.ssh 

# install strongdm client
RUN curl -J -O -L https://app.strongdm.com/releases/cli/linux  && \
    mv sdmcli* sdmcli.zip && \
    unzip sdmcli.zip && \
    rm sdmcli.zip

# docker build --build-arg SSH_PRV_KEY="$SSH_PRV_KEY" - < ./sdm_audit.Dockerfile
ARG SSH_PRV_KEY
RUN echo "$SSH_PRV_KEY" >  ~/.ssh/id_rsa && eval $(ssh-agent) && \
    chmod 600  ~/.ssh/id_rsa && ssh-add ~/.ssh/id_rsa && \
    ssh-keyscan -H github.com >> ~/.ssh/known_hosts  && \
    git clone git@github.com:Roblox/strongdm-nomad.git && \
    rm -r ~/.ssh/id_rsa

RUN cd strongdm-nomad && pip3 install -r requirements.txt && \
    pip3 install . && \
    cp scripts/sdm_log_svc.py ../sdm_log_svc.py && \
    pip3 install ipython

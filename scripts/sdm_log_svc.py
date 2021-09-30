from sdm_vault_automation import vault_management as vault
from sdm_vault_automation import strongdm_management as sdm
from sdm_vault_automation import sdm_vault


from datetime import datetime, timedelta
from dateutil.parser import parse as dt_parse
import logging
import traceback
import json
import os
import argparse
import urllib3
import subprocess
import shlex
import sys
import time

urllib3.disable_warnings()

LOG_FILE = "./sdm_log_svc.log"
LOGGER = logging.getLogger('sdm_log_svc')
HANDLER = logging.FileHandler(LOG_FILE)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.DEBUG)

create_truncated_iso = lambda secs : (datetime.utcnow() - timedelta(seconds=secs)).isoformat() + 'Z'

VAULT_TOKEN = os.environ.get('VAULT_TOKEN', None)
VAULT_ADDR = os.environ.get('VAULT_ADDR', None)
VAULT_BPATH = os.environ.get('VAULT_BPATH', None)
SDM_ADMIN_TOKEN_NAME = os.environ.get('SDM_ADMIN_TOKEN_NAME', "sdm_audit_admin")
AUDIT_START = os.environ.get('AUDIT_START', create_truncated_iso(0))
DEFAULT_SLEEP = os.environ.get('DEFAULT_SLEEP', 60.0)
DEFAULT_OUTPUT = os.environ.get('DEFAULT_OUTPUT', "/opt/logs/strongdm.json")
FLEET_TOKEN_NAME = os.environ.get('FLEET_TOKEN_NAME', "fleet")


ONE_GB = 10**9


SDM_AUDIT_COMMAND_FMT = "./sdm audit activities -j -e --from {}"


parser = argparse.ArgumentParser(description='Create StrongDM Setup.')
parser.add_argument('-vault_addr', type=str, default=VAULT_ADDR, help='set vault_addr')
parser.add_argument('-vault_token', type=str, default=VAULT_TOKEN, help='set vault_token')
parser.add_argument('-vault_bpath', type=str, default=VAULT_BPATH, help='set vault base path')

parser.add_argument('-sdm_tokenname', type=str, default=SDM_ADMIN_TOKEN_NAME, help='set strongdm API keys from vault')

parser.add_argument('-start', type=str, default=AUDIT_START, help='isoformat YYYY-MM-DDTHH:MM:SS.000000Z')
parser.add_argument('-sleep', type=float, default=DEFAULT_SLEEP, help='number of seconds to sleep between poll')
parser.add_argument('-output_file', type=str, default=DEFAULT_OUTPUT, help='output file to poll')

parser.add_argument('-fleet_tokenname', type=str, default=FLEET_TOKEN_NAME, help='set strongdm API keys from vault')

DEFAULT_PATH_ELASTIC_AGENT = os.environ.get("DEFAULT_PATH_ELASTIC_AGENT", "/opt/elastic-agent-linux/")
os.environ['DEFAULT_PATH_ELASTIC_AGENT'] = DEFAULT_PATH_ELASTIC_AGENT
ELASTIC_PROCESS = None
ELASTIC_COMMAND_FMT = "{DEFAULT_PATH_ELASTIC_AGENT}/elastic-agent install -f --url={FLEET_URL} --enrollment-token={FLEET_ENROLLMENT_TOKEN}"

SENT_1 = b'Successfully enrolled'
SENT_2 = b'successfully installed'

# start the elasticagent with the audit code
def start_elatic_agent():
    LOGGER.info("Starting elastic agent.")
    cmd_line = ELASTIC_COMMAND_FMT.format(**os.environ)
    cargs = shlex.split(cmd_line)
    ELASTIC_PROCESS = subprocess.Popen(cargs, stdout=subprocess.PIPE)
    ELASTIC_PROCESS.wait()
    data = ELASTIC_PROCESS.stdout.read()
    if data.find(SENT_1) > -1 and  data.find(SENT_2) > -1:
        LOGGER.info("Successfully installed and started the Fleet agent.")
    else:
        raise Exception("Unable to start the agent")


def poll_logs(last, output_file):
    cmd_line = SDM_AUDIT_COMMAND_FMT.format(last)
    cargs = shlex.split(cmd_line)
    try:
        LOGGER.debug("Polling StrongDM Control Plane for activities.")
        proc = subprocess.Popen(cargs, stdout=subprocess.PIPE)
    except:
        LOGGER.error("Process failed to execute command: {}".format(cmd_line))
        return last

    cnt = 0
    out = open(output_file, 'a')
    for line in proc.stdout.readlines():
        data = json.loads(line)
        last = data['timestamp']
        out.write(json.dumps(data)+'\n')
        out.flush()
        cnt += 1
    out.close()
    LOGGER.debug("Processed {} new events, next time stamp is: {}.".format(cnt, last))
    return last

if __name__ == "__main__":
    args = parser.parse_args()
    output_file = args.output_file
    LOGGER.info("Starting up.")
    try:
        base_path = args.vault_bpath
        #0. get the SDM API key from vault
        LOGGER.info("Initializing Vault Variables.")
        vault.initialize_environ(args.vault_addr, args.vault_token)
        LOGGER.info("Initializing SDM Variables.")
        sdm_vault.initialize_strongdm_token_from_vault(base_path, args.sdm_tokenname)
    except:
        LOGGER.critical("Failed to configure SDM_ADMIN_TOKEN: failing")
        # traceback.print_exc()
        LOGGER.critical(traceback.format_exc().replace('\n', ''))
        sys.exit(-1)

    try:
        LOGGER.info("Initializing FLeet Variables.")
        sdm_vault.initialize_strongdm_fleet_from_vault(base_path, args.fleet_tokenname)
        start_elatic_agent()
    except:
        LOGGER.critical("Failed to configure FLEET_ENROLLMENT_TOKEN: failing")
        # traceback.print_exc()
        LOGGER.critical(traceback.format_exc().replace('\n', ''))
        sys.exit(-1)

    last = args.start
    try:
        dt_parse(last)
    except:
        last = create_truncated_iso(0)
        LOGGER.warning("Invalid date format provided using: {}".format(last))


    while True:
        # check_agent()
        last = poll_logs(last, output_file)
        log_file_size = os.path.getsize(LOG_FILE)
        # print('log size is : ', log_file_size)        
        # check file size .5GB and if so keep only the last 100 lines
        if log_file_size > int(ONE_GB / 2):
            data = open(LOG_FILE).readlines()
            open(LOG_FILE, 'w').write("".join(data[:-100]))

        # check file size 1GB and if so truncate it
        file_size = os.path.getsize(output_file)
        # print('file size is : ', file_size)
        if file_size > ONE_GB:
           # sleep for 4 times polling
           time.sleep(4*args.sleep)
           # truncate the file
           x = open(output_file, 'w')
           x.close()
        else:
            time.sleep(args.sleep)



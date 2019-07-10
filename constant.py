from config import IP
import platform
#CMD_PREFIX = "docker exec nodeosd cleos --wallet-url http://%s:8900" % IP
if platform.uname()[0] == 'Darwin':
    CMD_PREFIX = "docker exec nodeosd cleos"
    CMD_PREFIX_KEOSD = "docker exec nodeosd"
else:
    CMD_PREFIX = "sudo docker exec nodeosd cleos"
    CMD_PREFIX_KEOSD = "sudo docker exec nodeosd"
SYSTEM_ACCOUNTS = ['eosio.bpay',
'eosio.token',
'eosio.msig',
'eosio.names',
'eosio.ram',
'eosio.ramfee',
'eosio.saving',
'eosio.stake',
'eosio.vpay',
'eosio.wrap',
'eosio.rex',
'eosio.assert']
DOCKER_IMAGE = "eoslaomao/eos:1.8.0"
BIOS_DOCKER_COMPOSE = """
version: "3"

services:
  nodeosd:
    image: %s
    command: nodeos --config-dir /opt/eosio/bin/data-dir -d /opt/eosio/bin/data-dir --genesis-json /opt/eosio/bin/data-dir/genesis.json --contracts-console
    hostname: nodeosd
    container_name: nodeosd
    ports:
      - 8888:8888
      - 9876:9876
    expose:
      - "9876"
    volumes:
      - ./data/bios-node:/opt/eosio/bin/data-dir
""" % DOCKER_IMAGE

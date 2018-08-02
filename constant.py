from config import IP
#CMD_PREFIX = "docker exec nodeosd cleos --wallet-url http://%s:8900" % IP
CMD_PREFIX = "docker exec nodeosd cleos"
CMD_PREFIX_KEOSD = "docker exec nodeosd"
SYSTEM_ACCOUNTS = ['eosio.bpay',
'eosio.msig',
'eosio.names',
'eosio.ram',
'eosio.ramfee',
'eosio.saving',
'eosio.stake',
'eosio.vpay']
DOCKER_IMAGE = "eoslaomao/eos:mainnet-1.1.1"
BIOS_DOCKER_COMPOSE = """
version: "3"

services:
  nodeosd:
    image: %s
    command: nodeosd.sh --data-dir "/opt/eosio/bin/data-dir" --genesis-json "/opt/eosio/bin/data-dir/genesis.json"
    hostname: nodeosd
    container_name: nodeosd
    ports:
      - 8888:8888
      - 9876:9876
    expose:
      - "9876"
    volumes:
      - /data/bios-node:/opt/eosio/bin/data-dir
""" % DOCKER_IMAGE

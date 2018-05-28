CMD_PREFIX = "docker exec nodeosd /usr/local/bin/cleos"
SYS_ACCOUNTS = ['eosio.bpay',
'eosio.msig',
'eosio.names',
'eosio.ram',
'eosio.ramfee',
'eosio.saving',
'eosio.stake',
'eosio.token',
'eosio.upay']
BIOS_DOCKER_COMPOSE = """
version: "3"

services:
  nodeosd:
    image: johnnyzhao/eosio-dawn-v4.2.0
    command: /usr/local/bin/nodeosd.sh --data-dir /opt/eosio/bin/data-dir --genesis-json /opt/eosio/bin/data-dir/genesis.json --replay-blockchain
    hostname: nodeosd
    container_name: nodeosd
    ports:
      - 8888:8888
      - 9876:9876
    expose:
      - "9876"
    volumes:
      - /data/bios-node:/opt/eosio/bin/data-dir

"""

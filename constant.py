from config import IP
CMD_PREFIX = "docker exec nodeosd cleos --wallet-url http://%s:8900" % IP
CMD_PREFIX_KEOSD = "docker exec keosd"
SYSTEM_ACCOUNTS = ['eosio.bpay',
'eosio.msig',
'eosio.names',
'eosio.ram',
'eosio.ramfee',
'eosio.saving',
'eosio.stake',
'eosio.vpay']
DOCKER_IMAGE = "johnnyzhao/eos:mainnet-1.0.6-unstake-in-5mins"
BIOS_DOCKER_COMPOSE = """
version: "3"

services:
  nodeosd:
    image: %s
    command: nodeosd.sh --data-dir /opt/eosio/bin/data-dir --replay-blockchain --filter-on "bankofmemory:release:" --genesis-json /opt/eosio/bin/data-dir/genesis.json --contracts-console
    hostname: nodeosd
    container_name: nodeosd
    ports:
      - 8888:8888
      - 9876:9876
    expose:
      - "9876"
    volumes:
      - /data/bios-node:/opt/eosio/bin/data-dir
  keosd:
    image: %s
    command: /opt/eosio/bin/keosd --wallet-dir /opt/eosio/bin/data-dir --http-server-address=0.0.0.0:8900
    hostname: keosd
    container_name: keosd
    ports:
      - 8900:8900
    links:
      - nodeosd
    volumes:
      - /data/keosd:/opt/eosio/bin/data-dir

""" % (DOCKER_IMAGE,DOCKER_IMAGE)

CMD_PREFIX = "docker exec nodeosd /usr/local/bin/cleos"
BIOS_DOCKER_COMPOSE = """
version: "3"

services:
  nodeosd:
    image: johnnyzhao/eosio-dawn-v4.1.0
    command: /usr/local/bin/nodeosd.sh --data-dir /opt/eosio/bin/data-dir --replay-blockchain
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

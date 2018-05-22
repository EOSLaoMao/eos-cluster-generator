#!/usr/bin/python
import os
from shutil import copyfile

tmpl = """
  nodeosd{index}:
    image: johnnyzhao/eosio-dawn-v4.1.0
    command: /usr/local/bin/nodeosd.sh --data-dir /opt/eosio/bin/data-dir
    hostname: nodeosd
    ports:
      - {port}:{port}
    expose:
      - "{port}"
    volumes:
      - /data/eos-bp{index}/:/opt/eosio/bin/data-dir
"""

keys = []
with open('keys') as key_file:
    for line in key_file:
        keys.append(line.strip())

m = {'0': 'a', '6': 'b', '7': 'c', '8': 'd', '9': 'e'}
account_script = open('create_account.sh', 'w')
reg_script = open('reg_producer.sh', 'w')
f = open('result', 'w')
prods = []
port = 9875
for i in range(0, 5):
    bp_name = ''.join([m[char] if char in m.keys() else char for char in 'bp%d' % i])
    line = tmpl.format(index=i, port=port)
    d = '/data/eos-bp{index}'.format(index=i)
    print(d)
    if not os.path.exists(d):
    	os.mkdir(d)
    f.write(line)
    genesis = os.path.join(d, 'genesis.json')
    copyfile('./genesis.json', genesis)
    config_dest = os.path.join(d, 'config.ini')
    config_tmpl = open('./config.ini').read()
    config = config_tmpl.format(bp_name=bp_name, port=port, key=keys[i-4])
    pub, pri = eval(keys[i-4].split('=')[1])
    cmd = 'docker exec opt_nodeosd_1 /usr/local/bin/cleos system newaccount eosio {bp_name} {pub} {pub} --stake-net "10.0000 SYS" --stake-cpu "10.0000 SYS" --buy-ram-bytes "128 KiB"\n'
    account_script.write(cmd.format(pub=pub, bp_name=bp_name))
    cmd = 'docker exec opt_nodeosd_1 /usr/local/bin/cleos wallet import {pri}\n'
    reg_script.write(cmd.format(pri=pri))
    cmd = 'docker exec opt_nodeosd_1 /usr/local/bin/cleos system regproducer {bp_name} {pub}\n'
    prods.append(bp_name)
    reg_script.write(cmd.format(pub=pub, bp_name=bp_name))
    with open(config_dest, 'w') as dest:
        dest.write(config)
    port -= 1
f.close()
account_script.close()
reg_script.close()
print(prods)

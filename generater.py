#!/usr/bin/python
import os
import random
from shutil import copyfile

def process_keys(f, as_list=True):
    keys = []
    key_pair = {}
    key_pairs = []
    with open(f) as key_file:
        for line in key_file:
            name, key = line.strip().split(': ')
            if not key_pair.has_key(name):
                key_pair[name] = key
            if len(key_pair.keys()) == 2:
                key_line = 'private-key = ["%s", "%s"]'
                keys.append(key_line % (key_pair['Public key'], key_pair['Private key']))
                key_pairs.append(key_pair)
                key_pair = {}
    return keys if as_list else key_pairs

def generate():
    bios = """
    version: "3"

    services:
      nodeosd:
        image: johnnyzhao/eosio-dawn-v4.1.0
        command: /usr/local/bin/nodeosd.sh --data-dir /opt/eosio/bin/data-dir --replay-blockchain
        hostname: nodeosd
        ports:
          - 8888:8888
          - 9876:9876
        expose:
          - "9876"
        volumes:
          - /data/bios-node:/opt/eosio/bin/data-dir

    """


    bios_keys = process_keys('bios_keys')
    print bios_keys
    f = open('docker-compose.yml', 'w')
    f.write(bios)
    d = '/data/bios-node'
    if not os.path.exists(d):
        os.mkdir(d)
    genesis = os.path.join(d, 'genesis.json')
    copyfile('./genesis.json', genesis)
    config_dest = os.path.join(d, 'config.ini')
    config_tmpl = open('./config.ini').read()
    peers = ['p2p-peer-address = 192.168.1.167:9876']
    config = config_tmpl.format(bp_name='eosio', port='9876', key=bios_keys[0], peers='\n'.join(peers), stale_production='true')
    config += '\nhttp-server-address = 0.0.0.0:8888'
    with open(config_dest, 'w') as dest:
        dest.write(config)
     
    tmpl = open('docker-compose-tmpl').read()
    keys = process_keys('keys')
    print keys

    m = {'0': 'a', '6': 'b', '7': 'c', '8': 'd', '9': 'e'}
    account_script = open('create_account.sh', 'w')
    reg_script = open('reg_producer.sh', 'w')
    prods = []
    port = 9875
    peer_prefix = 'p2p-peer-address = 192.168.1.167'
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
        config = config_tmpl.format(bp_name=bp_name, port=port, key=keys[i], peers='\n'.join(peers), stale_production='false')
        pub, pri = eval(keys[i].split('=')[1])
        cmd = 'docker exec opt_nodeosd_1 /usr/local/bin/cleos system newaccount eosio {bp_name} {pub} {pub} --stake-net "10.0000 SYS" --stake-cpu "10.0000 SYS" --buy-ram-bytes "128 KiB"\n'
        account_script.write(cmd.format(pub=pub, bp_name=bp_name))
        cmd = 'docker exec opt_nodeosd_1 /usr/local/bin/cleos wallet import {pri}\n'
        reg_script.write(cmd.format(pri=pri))
        cmd = 'docker exec opt_nodeosd_1 /usr/local/bin/cleos system regproducer {bp_name} {pub}\n'
        prods.append(bp_name)
        reg_script.write(cmd.format(pub=pub, bp_name=bp_name))
        with open(config_dest, 'w') as dest:
            dest.write(config)
        peers.append('%s:%d' % (peer_prefix, port))
        port -= 1
    f.close()
    account_script.close()
    reg_script.close()
    print(prods)
    return prods


def generate_voters(prods):
    voter_keys = process_keys('voter_keys', as_list=False)
    account_script = open('create_voter_account.sh', 'w')
    token_script = open('issue_voter_token.sh', 'w')
    delegate_script = open('delegate_voter_token.sh', 'w')
    vote_script = open('vote.sh', 'w')
    import_script = open('import_voter_keys.sh', 'w')
    print voter_keys
    i = 0
    for key_pair in voter_keys:
        i += 1
        account = 'voters%d' % i
        pub = key_pair['Public key']
        priv = key_pair['Private key']
        cmd = 'docker exec opt_nodeosd_1 /usr/local/bin/cleos system newaccount eosio {bp_name} {pub} {pub} --stake-net "10.0000 SYS" --stake-cpu "10.0000 SYS" --buy-ram-bytes "128 KiB"\n'
        account_script.write(cmd.format(pub=pub, bp_name=account))
        cmd = '''docker exec opt_nodeosd_1 /usr/local/bin/cleos push action eosio.token issue '{"to":"%s","quantity":"50000000.0000 SYS","memo":"issue"}' -p eosio\n''' % account
        token_script.write(cmd)
        cmd = 'docker exec opt_nodeosd_1 /usr/local/bin/cleos wallet import %s\n' % priv
        import_script.write(cmd)
        random.shuffle(prods)
        bps = ' '.join(prods[:len(prods)-2])
        cmd = 'docker exec opt_nodeosd_1 /usr/local/bin/cleos system voteproducer prods %s %s\n' % (account, bps)
        vote_script.write(cmd)
        cmd = "docker exec opt_nodeosd_1 /usr/local/bin/cleos system delegatebw %s %s '25000000 SYS' '25000000 SYS' --transfer\n" % (account, account)
        delegate_script.write(cmd)
    account_script.close()
    token_script.close()
    import_script.close()
    vote_script.close()
    delegate_script.close()


if __name__ == '__main__':
    prods = generate()
    generate_voters(prods)


#!/usr/bin/python
import os
import random
from shutil import copyfile
from config import IP
from constant import BIOS_DOCKER_COMPOSE, CMD_PREFIX, SYS_ACCOUNTS


def cmd_wrapper(cmd):
    return " ".join([CMD_PREFIX, cmd, '\n'])

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
    f = open('docker-compose.yml', 'w')
    f.write(BIOS_DOCKER_COMPOSE)
    d = '/data/bios-node'
    if not os.path.exists(d):
        os.mkdir(d)

    genesis = open('./genesis.json', 'w')
    pub_key = process_keys('bios_keys', as_list=False)[0]['Public key']
    content = open('./genesis-tmpl').read().replace('PUBKEY', pub_key)
    print content, pub_key
    genesis.write(content)
    genesis.close()

    dest_genesis = os.path.join(d, 'genesis.json')
    copyfile('./genesis.json', dest_genesis)
    config_dest = os.path.join(d, 'config.ini')
    config_tmpl = open('./config.ini').read()
    peers = ['p2p-peer-address = %s:9876' % IP]
    bios_keys = process_keys('bios_keys')
    config = config_tmpl.format(bp_name='eosio', port='9876', key=bios_keys[0], peers='\n'.join(peers), stale_production='true')
    config += '\nhttp-server-address = 0.0.0.0:8888'
    with open(config_dest, 'w') as dest:
        dest.write(config)
     
    tmpl = open('docker-compose-tmpl').read()
    keys = process_keys('bp_keys')

    m = {'0': 'a', '6': 'b', '7': 'c', '8': 'd', '9': 'e'}
    account_script = open('02_create_accounts.sh', 'aw')
    reg_script = open('03_reg_producers.sh', 'w')
    prods = []
    port = 9875
    peer_prefix = 'p2p-peer-address = %s' % IP

    for i in range(0, len(keys)):
        bp_name = ''.join([m[char] if char in m.keys() else char for char in 'bp%d' % i])
        prods.append(bp_name)
        line = tmpl.format(index=i, port=port)
        d = '/data/eos-bp{index}'.format(index=i)
        if not os.path.exists(d):
            os.mkdir(d)
        f.write(line)
        genesis = os.path.join(d, 'genesis.json')
        copyfile('./genesis.json', genesis)
        config_dest = os.path.join(d, 'config.ini')
        config_tmpl = open('./config.ini').read()
        config = config_tmpl.format(bp_name=bp_name, port=port, key=keys[i], peers='\n'.join(peers), stale_production='false')
        pub, pri = eval(keys[i].split('=')[1])
        cmd = 'system newaccount eosio {bp_name} {pub} {pub} --stake-net "10.0000 SYS" --stake-cpu "10.0000 SYS" --buy-ram-kbytes "128 KiB"'
        account_script.write(cmd_wrapper(cmd.format(pub=pub, bp_name=bp_name)))
        cmd = 'system regproducer {bp_name} {pub}'
        reg_script.write(cmd_wrapper(cmd.format(pub=pub, bp_name=bp_name)))
        with open(config_dest, 'w') as dest:
            dest.write(config)
        peers.append('%s:%d' % (peer_prefix, port))
        port -= 1
    f.close()
    account_script.close()
    reg_script.close()
    return prods


def generate_import_script():
    keys = []
    for f in ['token_keys', 'bios_keys', 'bp_keys', 'voter_keys']:
        keys.extend(process_keys(f, as_list=False))
    import_script = open('00_import_keys.sh', 'w')
    for key_pair in keys:
        pub = key_pair['Public key']
        priv = key_pair['Private key']
        cmd = 'wallet import %s || true' % priv
        import_script.write(cmd_wrapper(cmd))
    import_script.close()

def generate_voters(prods):
    voter_keys = process_keys('voter_keys', as_list=False)
    account_script = open('02_create_accounts.sh', 'aw')
    token_script = open('04_issue_voter_token.sh', 'w')
    delegate_script = open('05_delegate_voter_token.sh', 'w')
    vote_script = open('06_vote.sh', 'w')
    i = 0
    for key_pair in voter_keys:
        i += 1
        account = 'voters%d' % i
        pub = key_pair['Public key']
        priv = key_pair['Private key']
        cmd = 'system newaccount eosio {bp_name} {pub} {pub} --stake-net "10.0000 SYS" --stake-cpu "10.0000 SYS" --buy-ram-kbytes "128 KiB"'
        account_script.write(cmd_wrapper(cmd.format(pub=pub, bp_name=account)))
        cmd = """push action eosio.token issue '{"to":"%s","quantity":"50000000.0000 SYS","memo":"issue"}' -p eosio""" % account
        token_script.write(cmd_wrapper(cmd))
        random.shuffle(prods)
        bps = ' '.join(prods[:len(prods)-2])
        cmd = 'system voteproducer prods %s %s' % (account, bps)
        vote_script.write(cmd_wrapper(cmd))
        cmd = 'system delegatebw %s %s "25000000 SYS" "25000000 SYS" --transfer' % (account, account)
        delegate_script.write(cmd_wrapper(cmd))
    account_script.close()
    token_script.close()
    vote_script.close()
    delegate_script.close()

def generate_eosio_token():
    eosio_script = open('01_create_token.sh', 'aw')
    voter_keys = process_keys('token_keys', as_list=False)
    pub = voter_keys[0]['Public key']
    priv = voter_keys[0]['Private key']
    cmd = cmd_wrapper('set contract eosio.token contracts/eosio.token')
    cmd += cmd_wrapper("""push action eosio.token create '{"issuer":"eosio", "maximum_supply": "1000000000.0000 SYS", "can_freeze": 0, "can_recall": 0, "can_whitelist": 0}' -p eosio.token""")
    cmd += cmd_wrapper("""push action eosio.token issue '{"to":"eosio","quantity":"100000000.0000 SYS","memo":"issue"}' -p eosio""")
    cmd += cmd_wrapper("set contract eosio contracts/eosio.system")
    eosio_script.write(cmd)
    eosio_script.close()

def generate_sys_accounts():
    # generate sys account
    eosio_script = open('01_create_token.sh', 'w')

    pub = process_keys('token_keys', as_list=False)[0]['Public key']
    eosio_script.write(cmd_wrapper('set contract eosio contracts/eosio.bios'))
    eosio_script.write(cmd_wrapper('create account eosio eosio.token {pub} {pub}'.format(pub=pub)))

    pub = process_keys('bios_keys', as_list=False)[0]['Public key']
    for account in SYS_ACCOUNTS:
        cmd = 'create account eosio {account} {pub} {pub}'
        eosio_script.write(cmd_wrapper(cmd.format(pub=pub, account=account)))
    eosio_script.close()


if __name__ == '__main__':
    os.system("rm *.sh")
    generate_sys_accounts()
    generate_eosio_token()
    prods = generate()
    generate_voters(prods)
    generate_import_script()
    os.system("chmod u+x *.sh")

#!/usr/bin/python
import os
import random
from shutil import copyfile
from config import IP
from constant import (BIOS_DOCKER_COMPOSE,
                      CMD_PREFIX,
                      CMD_PREFIX_KEOSD,
                      SYSTEM_ACCOUNTS,
                      DOCKER_IMAGE,
                      DOCKER_IMAGE_ONE_SEVEN)

FILES = [
    '00_import_keys.sh',
    '01_create_token.sh',
    '02_create_accounts.sh',
    '03_reg_producers.sh',
    '04_issue_voter_token.sh',
    '05_delegate_voter_token.sh',
    '06_vote.sh',
]
WALLET_SCRIPT = "create_wallet.sh"

def cmd_wrapper(cmd, prefix=CMD_PREFIX):
    return " ".join([prefix, cmd, '\n'])

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
                #key_line = 'private-key = ["%s", "%s"]'
                key_line = 'signature-provider=%s=KEY:%s'
                keys.append(key_line % (key_pair['Public key'], key_pair['Private key']))
                key_pairs.append(key_pair)
                key_pair = {}
    return keys if as_list else key_pairs

def generate_peers(p=0):
    port = 9875
    peer_prefix = 'p2p-peer-address = %s' % IP
    peers = ['p2p-peer-address = %s:9876' % IP]

    keys = process_keys('bp_keys')
    for i in range(0, len(keys)):
        if port != p:
            peers.append('%s:%d' % (peer_prefix, port))
        port -= 1
    return peers



def generate():
    f = open('docker-compose.yml', 'w')
    f.write(BIOS_DOCKER_COMPOSE)
    d = './data/bios-node'
    if not os.path.exists(d):
        os.mkdir(d)

    genesis = open('./genesis.json', 'w')
    pub_key = process_keys('bios_keys', as_list=False)[0]['Public key']
    content = open('./genesis-tmpl').read().replace('PUBKEY', pub_key)
    # print content, pub_key
    genesis.write(content)
    genesis.close()

    dest_genesis = os.path.join(d, 'genesis.json')
    copyfile('./genesis.json', dest_genesis)
    bios_config_dest = os.path.join(d, 'config.ini')
    config_tmpl = open('./config.ini').read()
    bios_keys = process_keys('bios_keys')

     
    tmpl = open('docker-compose-tmpl').read()
    keys = process_keys('bp_keys')
    num_one_eight_bp = int(open('one_eight_bps').read().strip())

    m = {'0': 'a', '6': 'b', '7': 'c', '8': 'd', '9': 'e'}
    account_script = open(FILES[2], 'aw')
    reg_script = open(FILES[3], 'w')
    prods = []
    port = 9875
    peer_prefix = 'p2p-peer-address = %s' % IP


    #keys = process_keys('bp_keys')
    for i in range(0, len(keys)):
        image = DOCKER_IMAGE if num_one_eight_bp > 0 else DOCKER_IMAGE_ONE_SEVEN
        num_one_eight_bp -= 1
        bp_name = ''.join([m[char] if char in m.keys() else char for char in 'bp%d' % i])
        prods.append(bp_name)
        http_port = port - 1000
        line = tmpl.format(name=bp_name, port=port, http_port=http_port, image=image)
        d = './data/eos-{name}'.format(name=bp_name)
        if not os.path.exists(d):
            os.mkdir(d)
        f.write(line)
        genesis = os.path.join(d, 'genesis.json')
        copyfile('./genesis.json', genesis)
        config_dest = os.path.join(d, 'config.ini')
        config_tmpl = open('./config.ini').read()
        peers = generate_peers(port)
        config = config_tmpl.format(bp_name=bp_name, port=port, http_port=http_port, key=keys[i], peers='\n'.join(peers), stale_production='false')
        pub = keys[i].split('=')[1]
        pri = keys[i].split('=')[2][:3]
        cmd = 'system newaccount eosio {bp_name} {pub} {pub} --stake-net "10000.0000 EOS" --stake-cpu "10000.0000 EOS" --buy-ram-kbytes "128000 KiB"'
        account_script.write(cmd_wrapper(cmd.format(pub=pub, bp_name=bp_name)))
        cmd = 'system regproducer {bp_name} {pub}'
        reg_script.write(cmd_wrapper(cmd.format(pub=pub, bp_name=bp_name)))
        with open(config_dest, 'w') as dest:
            dest.write(config)
        #peers.append('%s:%d' % (peer_prefix, port))
        port -= 1

    # generate bios node config
    peers = generate_peers()
    bios_config = config_tmpl.format(bp_name='eosio', port='9876', http_port='8888', key=bios_keys[0], peers='\n'.join(peers), stale_production='true')
    with open(bios_config_dest, 'w') as dest:
        dest.write(bios_config)

    f.close()
    account_script.close()
    reg_script.close()
    return prods


def generate_import_script():
    keys = []
    for f in ['bios_keys', 'bp_keys', 'voter_keys']:
        keys.extend(process_keys(f, as_list=False))
    import_script = open(FILES[0], 'w')
    import_script.write("./%s\n" % WALLET_SCRIPT)
    for key_pair in keys:
        pub = key_pair['Public key']
        priv = key_pair['Private key']
        cmd = 'wallet import --private-key=%s || true' % priv
        import_script.write(cmd_wrapper(cmd))
    import_script.close()

def generate_voters(prods):
    voter_keys = process_keys('voter_keys', as_list=False)
    account_script = open(FILES[2], 'aw')
    token_script = open(FILES[4], 'w')
    delegate_script = open(FILES[5], 'w')
    vote_script = open(FILES[6], 'w')
    i = 0
    for key_pair in voter_keys:
        i += 1
        account = 'voter%d' % i
        pub = key_pair['Public key']
        priv = key_pair['Private key']
        cmd = 'system newaccount eosio {bp_name} {pub} {pub} --stake-net "10000.0000 EOS" --stake-cpu "10000.0000 EOS" --buy-ram-kbytes "128000 KiB"'
        account_script.write(cmd_wrapper(cmd.format(pub=pub, bp_name=account)))
        cmd = """push action eosio.token issue '{"to":"eosio","quantity":"60000000.0000 EOS","memo":"issue"}' -p eosio"""
        cmd = """transfer eosio %s "60000000.0000 EOS" -p eosio""" % account
        token_script.write(cmd_wrapper(cmd))
        random.shuffle(prods)
        if len(prods) > 2:
            bps = ' '.join(list(set(prods[:len(prods)-2])))
        else:
            bps = ' '.join(prods)
        cmd = 'system voteproducer prods %s %s' % (account, bps)
        vote_script.write(cmd_wrapper(cmd))
        cmd = 'system delegatebw %s %s "25000000 EOS" "25000000 EOS"' % (account, account)
        delegate_script.write(cmd_wrapper(cmd))
    account_script.close()
    token_script.close()
    vote_script.close()
    delegate_script.close()

def generate_eosio_token():
    eosio_script = open(FILES[1], 'aw')
    cmd = cmd_wrapper('set contract eosio.token contracts/eosio.token')
    cmd = cmd_wrapper('set contract eosio.token contracts/eosio.token')
    cmd += cmd_wrapper("""push action eosio.token create '{"issuer":"eosio", "maximum_supply": "1000000000.0000 EOS", "can_freeze": 0, "can_recall": 0, "can_whitelist": 0}' -p eosio.token""")
    cmd += cmd_wrapper("""push action eosio.token issue '{"to":"eosio","quantity":"200000000.0000 EOS","memo":"issue"}' -p eosio""")
    cmd += cmd_wrapper("set contract eosio.msig contracts/eosio.msig")
    cmd += cmd_wrapper("""push action eosio setpriv '{"account": "eosio.msig", "is_priv": 1}' -p eosio""")
    cmd += cmd_wrapper("set contract eosio contracts/eosio.system")
    cmd += cmd_wrapper("set contract eosio contracts/eosio.system")
    cmd += cmd_wrapper("set contract eosio contracts/eosio.system")
    cmd += cmd_wrapper("""push action eosio init '{"version": 0, "core": "4,EOS"}' -p eosio""")
    cmd += cmd_wrapper("set contract eosio.wrap contracts/eosio.wrap")
    cmd += cmd_wrapper("""push action eosio setpriv '{"account": "eosio.wrap", "is_priv": 1}' -p eosio""")
    eosio_script.write(cmd)
    eosio_script.close()

def generate_sys_accounts():
    # generate sys account
    eosio_script = open(FILES[1], 'w')

    eosio_script.write('docker cp contracts/1.6.1 nodeosd:/contracts\n')
    eosio_script.write(cmd_wrapper('set contract eosio contracts/eosio.bios'))

    pub = process_keys('bios_keys', as_list=False)[0]['Public key']
    for account in SYSTEM_ACCOUNTS:
        cmd = 'create account eosio {account} {pub} {pub}'
        eosio_script.write(cmd_wrapper(cmd.format(pub=pub, account=account)))
    eosio_script.close()

def generate_wallet_script():
    wallet_script = open(WALLET_SCRIPT, 'w')
    wallet_script.write(cmd_wrapper("sh -c 'rm /opt/eosio/bin/data-dir/default.wallet' || true", CMD_PREFIX_KEOSD))
    wallet_script.write(cmd_wrapper("sh -c 'rm ~/eosio-wallet/default.wallet' || true", CMD_PREFIX_KEOSD))
    wallet_script.write(cmd_wrapper("cleos wallet create -n default --to-console > wallet_password", CMD_PREFIX_KEOSD))
    wallet_script.close()

def generate_boot_script():
    start_script = open("boot.sh", 'w')
    start_script.write("docker-compose up -d\nsleep 2\n")
    #start_script.write('./activate.sh\nsleep 2\n')
    start_script.write("\nsleep 2\n".join(['./'+f for f in FILES]))
    start_script.close()

    bashrc_script = open("bashrc", 'w')
    bashrc_script.write('alias cleos="%s"' % CMD_PREFIX)
    bashrc_script.close()


if __name__ == '__main__':
    os.system("rm 0*.sh")
    os.system("mkdir data")
    generate_boot_script()
    generate_wallet_script()
    generate_sys_accounts()
    generate_eosio_token()
    prods = generate()
    generate_voters(prods)
    generate_import_script()
    os.system("chmod u+x *.sh")

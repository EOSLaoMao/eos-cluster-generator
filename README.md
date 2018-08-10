# EOS Cluster Generator

This tool is a Docker based local multi-bp config generater. You can use it to boot up an EOS testnet on your laptop in 5 minutes.


## Quick Start

### 1. Prepare /data directroy

We use `/data` dir as docker volume dir to store blockchain data, so make sure it's created and change owner to your current user.

```
sudo mkdir /data
sudo chown -R USERNAME /data
```

### 2. Run `init.sh` to generate keys and configs

Run `init.sh`, will emit outputs as follows:

```
$ ./init.sh

Starting docker container eos-key-generator
c49a1993a069312e58268906cdd5586d2ec333775b6f014c829fad4ae2695568

(1/3) Generating 10 keys for BP account...
10 BP keys generated

(2/3) Generating 3 keys for voter accounts...
3 voter keys generated

(3/3) Generating configs under /data/ dir...
All set!
Now you can exec ./boot.sh to boot the network up!
```

First, it will run a eos-key-generator container to generate EOS keys for BP and Voter accounts. It will generate 10 BP keys and 3 voter keys by default, you can change it in `init.sh` script. But make sure voter accounts >= 3, since we hardcoded to issue 60M EOS token to each voter and stake 50M each(to activate the chain, 150M staked&voted EOS tokens needed). Note that we use an wellknown key "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV" for bios node located in `bios_key` file.

After keys generated, `init.sh` will continue to run `generate.py` script to generate configs for bios&BP nodes under `/data` dir, including `config.ini`, `genesis.json`, etc. `generate.py` will also generate a bunch of necessary bash scripts including `boot.sh` and other step-by-step scripts for manual use.


### 3. Run `boot.sh` to boot it up!


`boot.sh` scripts combines step-by-step script into one. It looks like this:

```
$ cat boot.sh

docker-compose up -d
sleep 2
./00_import_keys.sh
sleep 2
./01_create_token.sh
sleep 2
./02_create_accounts.sh
sleep 2
./03_reg_producers.sh
sleep 2
./04_issue_voter_token.sh
sleep 2
./05_delegate_voter_token.sh
sleep 2
./06_vote.sh
```

As you can see, `boot.sh` will first boot up docker containers as bios&BP nodes, then import keys, create EOS token, create necessary account, reg producer, issue token to voters and vote for producers.

After you run `boot.sh`, you will have a fully functional EOS blockchain. BP accounts will be like `bp1`, `bp2` ...... `bpz`, and voters as `voter1`, `voter2`, etc. Eeach voter account has 60M EOS with 50M staked. at this point, BPs will be generating blocks instead of bios node, too. You can check nodeos logs to verify that:

```
docker logs -f nodeosd
```


### 4. Resign `eosio` account

To fully simulate an EOS chain just like EOS Mainnet, you should resign all system account to `eosio.prods` permission. Functions like multisig proposal will only work after system account are properly resigned.

To resign system accounts, just run `resign.sh`

```
./resign.sh
```

Now, you have a full fledged EOS chain on your laptop!


### STOP and clear all the data

just run `destroy.sh`, it will bring all the nodes down and clear all the node data under `/data/`.

before you start over from step 1, please make sure you have ran `destroy.sh`.


## Alternative Manual Steps

### 1. Prepare key pairs

Clone this project and create 2 files namingly `bp_keys`, `voter_keys` under the directory of this repo. Note that we use an wellknown key "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV" for bios node and system accounts, so you don't need to specify `bios_key` or `token_keys` anymore.

Put key pair for BP and Voter accounts into file `bp_keys` and `voter_keys` using the format as follows:

```
Private key: 5HvwrfNLVw9bKFXXXXXXX
Public key: EOS7qfbpbAjqXXXXXXX
Private key: 5HvwrfNLVw9bKFXXXXXXX
Public key: EOS7qfbpbAjqXXXXXXX
```

it you want to SIMULATE VOTING WITH 21 BPs, YOU HAVE TO PROVIDE MORE THAN 21 KEY PAIRS IN `bp_keys`

Since we hardcoded to issue 60M tokens to each voter and only stake 50M each, at least 3 voter key pairs should be provided in `voter_keys` to achieve 15% trigger(150M EOS should be staked&vote to activate the chain).

Voter accounts are named like `voter1`, `voter2`, `voter3`, etc.

BP accounts are named like `bp1`, `bp2`, `bp3`, etc.


### 2. Prepare /data directroy

We use `/data` dir as docker volume dir, so make sure it's created and change owner to your current user.

```
sudo mkdir /data
sudo chown -R USERNAME /data
```

### 3. Generate!

When you prepared the keys properly, execute:

```
python generate.py
```

this command will generate the following files under project dir:

```
-rwxr--r--   1 john  staff  8226 May 23 16:28 boot.sh
-rwxr--r--   1 john  staff  8226 May 23 16:28 docker-compose.yml
-rwxr--r--   1 john  staff  3596 May 23 16:29 00_import_keys.sh
-rwxr--r--   1 john  staff   608 May 23 16:28 01_create_token.sh
-rwxr--r--   1 john  staff  7455 May 23 16:28 02_create_accounts.sh
-rwxr--r--   1 john  staff  2990 May 23 16:28 03_reg_producers.sh
-rwxr--r--   1 john  staff   584 May 23 16:28 04_issue_voter_token.sh
-rwxr--r--   1 john  staff   468 May 23 16:28 05_delegate_voter_token.sh
-rwxr--r--   1 john  staff   727 May 23 16:28 06_vote.sh

```

`docker-compose.yml` file contains the service you should start for bios-node and BP nodes.

`boot.sh` script is used to boot all the nodes up and inject necessery data to the chain, all the way to voting.

`bashrc` defines a alias for cleos, which is something like `alias cleos="docker exec nodeosd cleos --wallet-url=xxxxx"`

Lastly, these numbered bash scripts contains the necessery commands each step all the way to voting. if you would like to execute these command one by one, feel free to do that. The number in script names indicates the sequence.

Also, `generate.py` will generate data dirs and configs for each BP under `/data` dir.

### 4. RUN!

use `boot.sh` script to boot it up!

```
./boot.sh
```

Then you can check the log of `nodeosd` container, which is bios node. You should see `eosio` generating blocks pretty soon.

Next, you can further test BP failover, voting or anything functionality you want to play with!

There is an alias for `cleos` command in `bashrc`, simple source it teh you can call `cleos` to run all kinds of test.

```
source bashrc

cleos get account eosio
```

enjoy!

### STOP and clear all the data

just run `destroy.sh`, it will bring all the nodes down and clear all the node data under `/data/`

# EOS Cluster Generator

EOS Cluster Generator is a Docker based multi-bp config generater. You can use it to boot up an EOS testnet on your laptop in 5 minutes.

This branch is used to test 1.7 and 1.8 mixture network for upgrade only.


## Quick Start

### 1. Run `init.sh` to generate keys and configs

Run `init.sh` will generate 21 BPs with 15 of them on v1.8.3 and 6 on v1.7.5. 

You can specify num of BPs as the first param like this(default is 15):

```
$ ./init.sh {NUM_OF_BPS_ON_1.8.3}

Starting docker container eos-key-generator
c49a1993a069312e58268906cdd5586d2ec333775b6f014c829fad4ae2695568

This script will create configs for 21 BPs which will have {NUM_OF_BPS_ON_1.8.3} BPs on v1.8.3, others will be v1.7.3

(1/3) Generating 21 keys for BP account...
{NUM_BP} BP keys generated

(2/3) Generating 3 keys for voter accounts...
3 voter keys generated

(3/3) Generating configs under /data/ dir...
All set!
Now you can exec ./boot.sh to boot the network up!
```

First, it will run a eos-key-generator container to generate EOS keys for BP and Voter accounts. It will generate 3 BP keys and 3 voter keys by default, you can change it in `init.sh` script. But make sure voter accounts >= 3, since we hardcoded to issue 60M EOS token to each voter and stake 50M each(to activate the chain, 150M EOS staked&vote needed).

Note that we use an wellknown key "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV" for bios node located in `bios_key` file(You dont need to change it).

After keys generated, `init.sh` will continue to run `generate.py` script to generate configs for bios&BP nodes under `./data` dir, including `config.ini`, `genesis.json`, etc. `generate.py` will also generate a bunch of necessary bash scripts including `boot.sh` and other step-by-step scripts for mannual use.

Also, `docker-compose.yaml` will be generated which defines Docker containers for bios&BP nodes.


### 2. Run `boot.sh` to boot it up!


`boot.sh` combines step-by-step script into one. It looks like this:

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

As you can see, `boot.sh` will first boot up docker containers as bios&BP nodes, then import keys, create EOS token, create necessary accounts, reg producer, issue token to voters and vote for producers.

After you run `boot.sh`, you will have a fully functional EOS blockchain. BP accounts will be like `bp1`, `bp2` ...... `bpz`, and voters as `voter1`, `voter2`, etc. 

Each voter account has 60M EOS with 50M staked. At this point, BPs will be generating blocks instead of bios node, too. You can check nodeos logs to verify that:

```
docker logs -f nodeosd
```

Note that all the keys generated in step 1 are imported in `nodeosd` container, you can check the importion detail in `00_import_keys.sh`. Also, there is a `wallet_password` file created after the import which contains the password to unlock the default wallet in `nodeosd` container.


### 3. Resign `eosio` and other system accounts

To fully simulate an EOS chain just like EOS Mainnet, you should resign all system accounts to `eosio.prods` permission. Functions like multisig proposal will only work after system accounts are properly resigned.

To resign system accounts, just run `resign.sh`

```
./resign.sh
```

Now, you have a full fledged EOS chain on your laptop!

### 4. Test 1.8 Activation

We have prepared scripts for you to activate 1.8:

```
./activate.sh
```

This script will try to activate 1.8 in this mixed network.

Please test it and report the result back to 1.8 upgration group.


### STOP and CLEAR

Before you start over from step 1, please make sure you have ran `destroy.sh`, it will bring bios&BP nodes down and rm `./data/` dir


## Alternative Mannual Steps(Specify keys mannually)

### 1. Prepare key pairs

Create 2 files namingly `bp_keys`, `voter_keys` under the directory of this repo. Note that we use a wellknown key "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV" for bios node and system accounts, so you don't need to specify `bios_key` or `token_keys` anymore.

Put key pairs for BP and Voter accounts into file `bp_keys` and `voter_keys` using the format as follows:

```
Private key: 5HvwrfNLVw9bKFXXXXXXX
Public key: EOS7qfbpbAjqXXXXXXX
Private key: 5HvwrfNLVw9bKFXXXXXXX
Public key: EOS7qfbpbAjqXXXXXXX
```

NOTE: If you want to SIMULATE VOTING WITH 21 BPs, YOU HAVE TO PROVIDE MORE THAN 21 KEY PAIRS IN `bp_keys`

Since we hardcoded to issue 60M tokens to each voter and only stake 50M each, at least 3 voter key pairs should be provided in `voter_keys` to achieve 15% trigger(150M EOS should be staked&vote to activate the chain).

Voter accounts are named like `voter1`, `voter2`, `voter3`, etc.

BP accounts are named like `bp1`, `bp2`, `bp3`, etc.


### 2. Generate configs

After keys prepared properly, execute:

```
python generate.py
```

This script will generate the following files under project dir:

```
-rwxr--r--   1 john  staff  8226 May 23 16:28 boot.sh
-rwxr--r--   1 john  staff  8226 May 23 16:28 bashrc
-rwxr--r--   1 john  staff  8226 May 23 16:28 docker-compose.yml
-rwxr--r--   1 john  staff  3596 May 23 16:29 00_import_keys.sh
-rwxr--r--   1 john  staff   608 May 23 16:28 01_create_token.sh
-rwxr--r--   1 john  staff  7455 May 23 16:28 02_create_accounts.sh
-rwxr--r--   1 john  staff  2990 May 23 16:28 03_reg_producers.sh
-rwxr--r--   1 john  staff   584 May 23 16:28 04_issue_voter_token.sh
-rwxr--r--   1 john  staff   468 May 23 16:28 05_delegate_voter_token.sh
-rwxr--r--   1 john  staff   727 May 23 16:28 06_vote.sh

```

`docker-compose.yml` contains the service for bios&BP nodes.

`boot.sh` is used to boot all the nodes up and inject necessery data to the chain, all the way to voting.

`bashrc` defines an alias for cleos, something like `alias cleos="docker exec nodeosd cleos"`

Lastly, these numbered bash scripts contains the necessery commands each step all the way to voting. if you would like to execute these command one by one, feel free to do that. The number in script names indicates the sequence.

Also, `generate.py` will generate data dirs and configs for each BP under `./data` dir.

### 3. BOOT!

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

Enjoy!

### 4. Resign `eosio` and other system accounts

To fully simulate an EOS chain just like EOS Mainnet, you should resign all system accounts to `eosio.prods` permission. Functions like multisig proposal will only work after system accounts are properly resigned.

To resign system accounts, just run `resign.sh`

```
./resign.sh
```

Now, you have a full fledged EOS chain on your laptop!


### STOP and CLEAR

Before you start over from step 1, please make sure you have ran `destroy.sh`, it will bring bios&BP nodes down and rm `./data/` dir

# EOS Cluster Generator

This tool is a Docker based local multi-bp config generater. The only thing you need to provide is EOS key pairs.

### 1. Prepare key pairs

Clone this project and create 4 files namingly `bios_keys`, `token_keys`, `bp_keys`, `voter_keys` under the directory of this repo. 

Put bios node key pair and key pair for account `eosio.token` into file `bios_keys` and `token_keys` using the format as follows:

```
Private key: 5HvwrfNLVw9bKFXXXXXXX
Public key: EOS7qfbpbAjqXXXXXXX
```

Put key pairs of BPs and voters into file `bp_keys` and `voter_keys` using the same format as above.

TO SIMULATE VOTING WITH 21 BPs, YOU HAVE TO PROVIDE MORE THAN 21 KEY PAIRS IN `bp_keys`

Since we hardcode to issue 50M tokens to each voter, at least 3 voter key pairs should be provided in `voter_keys` to achieve 15% trigger.

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
-rwxr--r--   1 john  staff  8226 May 23 16:28 start.sh
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

`docker-compose.yml` file contains the service you should start for bios-node and BP nodes.

`start.sh` script is used to boot all the nodes up and inject necessery data to the chain, all the way to voting.

`bashrc` defines a alias for cleos, which is something like `alias cleos="docker exec nodeosd cleos --wallet-url=xxxxx"`

Lastly, these numbered bash scripts contains the necessery commands each step all the way to voting. if you would like to execute these command one by one, feel free to do that. The number in script names indicates the sequence.

Also, `generate.py` will generate data dirs for each BP under `/data` dir.

### 4. RUN!

use `start.sh` script to boot it up!

```
./start.sh
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

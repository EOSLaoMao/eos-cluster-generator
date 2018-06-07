# EOS Cluster Generator

This tool is a Docker based local multi-bp config generater. The only thing you need to provide is key pairs and some customizable configs.

For test purpose, this tool use a self built docker image with eos source code changed unstage timeframe from 3 days to 5 mins.

The image this tool use is : `heipacker2016/eos:v1.0.1-unstake-5-mins-eos`, as you can see, we have changed some paramaters to make sure you can get you tokens back in 5 mins. The change is here: https://github.com/EOSLaoMao/eos/pull/1/files

You should pull or build this image before continue.

### 0. Clone this project

Clone this project and change the `IP` to your host ip in `config.py`

### 1. Prepare key pairs

Create 4 files namingly `bios_keys`, `token_keys`, `bp_keys`, `voter_keys` under the directory of this project. 

Put bios node key pair and key pair for account `eosio.token` into file `bios_keys` and `token_keys` using the format as follows:

```
Private key: 5HvwrfNLVw9bKFXXXXXXX
Public key: EOS7qfbpbAjqXXXXXXX
```

Put key pairs of BPs and voters into file `bp_keys` and `voter_keys` using the same format as above. 

TO SIMULATE VOTING WITH 21 BPs, YOU HAVE TO PROVIDE MORE THAN 21 KEY PAIRS IN `bp_keys`

Since we hardcode to issue 50M tokens to each voter, at least 3 voter key pairs should be provided in `voter_keys` to achieve 15% trigger.


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

these bash scripts contains the necessery commands all the way to voting. The number in script names indicates the sequence.

Also, `generate.py` will generate data dirs for each BP under `/data` dir.

### 4. RUN!

first, use docker-compose to start bios and BP node containers.

```
docker-compose up -d
```

Then can check the log of `nodeosd` container, which is bios node. You should see `eosio` generating blocks pretty soon.

After that, you should create a wallet to import your keys.

```
docker exec nodeosd cleos wallet create
```

Then, run those numbered bash scripts one by one, all the way to voting.

After `06_vote.sh` executed, you can check the log of both BP and bios nodes. You should be seeing that bios node stopped producing blocks and top 21 BPs with largest voting numbers producing instead.

Next, you can further test BP failover or voting!

OR, you can test `unstake`, to make sure you can get your token back!

### 5. Test unstake in 5 mins with 1 command!!!

The only command you need to execute is `undelegatebw`:

```
docker exec nodeosd cleos system undelegatebw voters1 voters1 "100 EOS" "200 EOS"
```

and wait for 5 mins, then query your balance:

```
docker exec nodeosd cleos get currency balance eosio.token voters1
```

and the output should be:

```
300 EOS
```

### Conclusion

1. The voting works as expected.
2. The `delegatebw` and `undelegatebw` works as expected.
3. The network needs to reach 15% votings, until then, you cannot unstake all tokens.
4. staked tokens weather be used for voting or not, both can be unstaked after 15% voting readched.

Good luck with mainnet launching, guys!

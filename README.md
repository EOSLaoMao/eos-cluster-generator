# EOS Cluster Generator

This tool is a Docker based local multi-bp config generater. The only thing you need to provide is key pairs and some customizable configs.

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

Since we hardcode to issue 50M EOS to each voter, at least 3 voter key pairs should be provided in `voter_keys`.



### 2. Prepare /data directroy

We use `/data` dir as docker mounting dir, so make sure it's created and change owner to your current user.

```
sudo mkdir /data
sudo chown -R USERNAME /data
```

### 3. Generate!

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

`docker-compose.yml` file contains the service you should start for bios-node and bp nodes.

these bash scripts contains the necessery commands all the way to voting. The number in script names indicates the sequence.

Also, `generate.py` will generate data dirs for each BP under `/data` dir.

### 4. RUN!

first, using docker-compose to run bios and bp nodes.

```
docker-compose up -d
```

Then you can run those number bash scripts one by one.

After `06_vote.sh` executed, you can check the log of both bp nodes. You should be seeing that bios node stopped producing blocks and top 21 BPs with largest voting numbers producing instead.

Next, you can further test BP failover or voting!






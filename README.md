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


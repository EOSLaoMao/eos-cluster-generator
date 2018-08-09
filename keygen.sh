#!/bin/bash

#Docker image used to generate EOS keys
IMAGE=eoslaomao/eos:1.1.4

#Number of block producers, default is 10.
NUM_BPS=10

#Number of voters, default is 4. Each voter will have 50M EOS token
NUM_VOTERS=4

docker ps | grep eos-dev
if [ $? -ne 0 ]; then
    echo "Run eos dev env"
    docker run -d -it --name eos-dev $IMAGE /bin/bash
fi

touch bp_keys voter_keys

> bp_keys
> voter_keys

for (( c=0; c<$NUM_BPS; c++ ))
do
    docker exec eos-dev cleos create key >> bp_keys
done


for (( c=0; c<$NUM_VOTERS; c++ ))
do
    docker exec eos-dev cleos create key >> voter_keys
done

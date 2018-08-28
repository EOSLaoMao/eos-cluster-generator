#!/bin/bash

#Docker image used to generate EOS keys
IMAGE=eoslaomao/eos:1.2.2

#Number of block producers, default is 3.
NUM_BPS=3

#Number of voters, default is 3. Each voter will have 60M EOS token and 50M of it staked
NUM_VOTERS=3

CONTAINER=eos-key-generator


if [ $NUM_VOTERS -lt 3 ]; then
  echo "NUM_VOTERS must greater than 3 since every voters have 50M EOS staked"
  exit
fi

docker ps | grep $CONTAINER
if [ $? -ne 0 ]; then
    echo "Starting docker container $CONTAINER"
    docker run -d -it --name $CONTAINER $IMAGE /bin/bash
fi

echo

touch bp_keys voter_keys

> bp_keys
> voter_keys

echo "(1/3) Generating $NUM_BPS keys for BP account..."
for (( c=0; c<$NUM_BPS; c++ ))
do
    docker exec $CONTAINER cleos create key --to-console >> bp_keys
done
echo "$NUM_BPS BP keys generated"

echo

echo "(2/3) Generating $NUM_VOTERS keys for voter accounts..."
for (( c=0; c<$NUM_VOTERS; c++ ))
do
    docker exec $CONTAINER cleos create key --to-console >> voter_keys
done
echo "$NUM_VOTERS voter keys generated"

echo

echo "(3/3) Generating configs under /data/ dir..."
python generate.py

echo "All set!"
echo "Now you can exec ./boot.sh to boot the network up!"

docker stop $CONTAINER > /dev/null
docker rm $CONTAINER > /dev/null

docker-compose up -d
sleep 2
./activate.sh
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
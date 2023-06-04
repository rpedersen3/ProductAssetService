# product asset service

Product Asset service GraphQL API using Graphene in a Django server

## What is here
- Product Asset GraphQL API that integrates with ethereum product asset contracts
- GraphQL UI

## Using this

* python -m venv python-graphene-graphql-ve
* pip install -U pip
* pip install -r requirements.txt

## Run service:  startups service on http://127.0.0.1:5000
> cd c:\ethereum-nodes  
> flask run --host 0.0.0.


## Dependent on these local services

### IPFS local service
Setting up IPFS: https://www.richcanvas3.com/ipfs-vue-nft-attribute-display

To run ipfs on local host.  Can run this in any directory because it is globally defined
> ipfs daemon

### Ethereum Private Network local service
Setting up ethereum private network:  https://www.richcanvas3.com/ethereum-private-network

To run ethereum private network: Need to run this in c:\ethereum-nodes directory.
<poem>
> cd c:\ethereum-nodes
> geth --datadir node1 --port 30308 --bootnodes enode://dd56ba62106a591288316f5b487ac0fc84046ba5438fc4e18e8d1b24bd33a6f024e32dacaf76d90912aaa198a8bebb5b8b9d53ffa47ebfeef4fd25430e21a10a@127.0.0.1:0?discport=30305  --networkid 12345 --unlock 0x4FB0032AA225a94EdB257ae1d2338DfDc6d23e7F --password password.txt  --http --allow-insecure-unlock --http.corsdomain "*"  --http.vhosts "*" --http.addr "0.0.0.0" --authrpc.port 8560 --http.port 8546 --ipcpath=node1/geth.ipc --http.api="eth,net,web3,personal,web3" --rpc.enabledeprecatedpersonal --rpc.gascap 0 --rpc.txfeecap 0  --verbosity "4"
</poem
Then you need to startup another cmd prompt, startup geth client and startup miner.  Make sure you give the blockchain time to initialize.
> cd c:\ethereum-nodes
> geth attach \\.\pipe\node1\geth.ipc
> personal.unlockAccount(eth.accounts[0])
Passprase: password
> miner.setEtherbase("0x4FB0032AA225a94EdB257ae1d2338DfDc6d23e7F")
> miner.start(1)


### Redis Cache local service

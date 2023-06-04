# product asset service

Product Asset service GraphQL API using Graphene in a Django server

## What is here
- Product Asset GraphQL API that integrates with ethereum product asset contracts
- GraphQL UI

## Using this

> python -m venv python-graphene-graphql-ve <br />
> pip install -U pip <br />
> pip install -r requirements.txt <br />

## Run service:  startups service on http://127.0.0.1:5000
> cd c:\ethereum-nodes <br />
> flask run --host 0.0.0.0 <br />

You can now query this graphql api with: 
http://127.0.0.1:5000/graphql


## Dependent on these local services

### IPFS local service
Setting up IPFS: https://www.richcanvas3.com/ipfs-vue-nft-attribute-display

To run ipfs on local host.  Can run this in any directory because it is globally defined
> ipfs daemon

### Ethereum Private Network local service
Setting up ethereum private network:  https://www.richcanvas3.com/ethereum-private-network

To run ethereum private network: Need to run this in c:\ethereum-nodes directory.

> cd c:\ethereum-nodes <br />
> geth --datadir node1 --port 30308 --bootnodes enode://dd56ba62106a591288316f5b487ac0fc84046ba5438fc4e18e8d1b24bd33a6f024e32dacaf76d90912aaa198a8bebb5b8b9d53ffa47ebfeef4fd25430e21a10a@127.0.0.1:0?discport=30305  --networkid 12345 --unlock 0x4FB0032AA225a94EdB257ae1d2338DfDc6d23e7F --password password.txt  --http --allow-insecure-unlock --http.corsdomain "*"  --http.vhosts "*" --http.addr "0.0.0.0" --authrpc.port 8560 --http.port 8546 --ipcpath=node1/geth.ipc --http.api="eth,net,web3,personal,web3" --rpc.enabledeprecatedpersonal --rpc.gascap 0 --rpc.txfeecap 0  --verbosity "4" <br />

Then you need to startup another cmd prompt, startup geth client and startup miner.  Make sure you give the blockchain time to initialize.
> cd c:\ethereum-nodes <br />
> geth attach \\.\pipe\node1\geth.ipc <br />
> personal.unlockAccount(eth.accounts[0]) <br />
Passprase: password <br />
> miner.setEtherbase("0x4FB0032AA225a94EdB257ae1d2338DfDc6d23e7F") <br />
> miner.start(1) <br />


### Redis Cache local service
Setting up Redis: 

To startup redis you need to first go to ubuntu environment wsl.  Then startup redis
> wsl <br />
> sudo service redis-server start <br />
> enter: --find in linux credentials-- <br /> 
> redis-cli <br />

Redis should now be running on 127.0.0.1:6379


## Ethereum Contracts called by service

Contracts are found in C:\github\web3store\contracts

View these on visual studio code => remix extension


## GraphQL example queries

Synch decentraland assets "land" and "wearables" from OpenSea to this private network
<pre>
query {
  synchProducts  { 
    products  {
        name
    }
  }
}
</pre>

import json
import jsonschema
from jsonschema import validate

import re
import solcx
import array
import os

import graphene
from graphene import ObjectType

from web3 import Web3
from web3.middleware import geth_poa_middleware

import requests 

from owslib.ogcapi.features import Features as OGCFeature

from api_synch import SynchFilterInput, SynchSortInput

import ipfshttpclient


from attribute_type_metadata import AttributeTypeMetadata
from attribute_metadata import AttributeMetadata

from api_collection import Collection, Collections
from collection_metadata_schema import CollectionMetadataSchema
from collection_metadata import CollectionMetadata

from api_item import Item, Items
from item_metadata_schema import ItemMetadataSchema
from item_metadata import ItemMetadata
from attribute_type_metadata import AttributeTypeMetadata


from web3.gas_strategies.rpc import rpc_gas_price_strategy


import redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)



import logging
logger = logging.getLogger(__name__)



class SynchFeatures(graphene.Interface):

    items = graphene.List(Item)
    total_count = graphene.Int(required=True)

class SynchFeatureList(graphene.ObjectType):
    class Meta:
        interfaces = (Items,)



class SynchFeatureQuery(graphene.ObjectType):

    synch_features = graphene.Field(
        Items,
        filter=graphene.Argument(SynchFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(SynchSortInput, default_value={})
    )
    
    @staticmethod
    def resolve_synch_features(self, info, filter, current_page, page_size, search, sort):
        #print("(Rich) resolve_synch_features => get features: ")
        items, total_count = synch_feature_list(
            current_page, page_size, search, sort, **filter)
        
        #print("(Rich) resolve_features => get features return list: ")
        return SynchFeatureList(items=items, total_count=total_count)
    

def validate_json(json_data, json_schema):

    try:
        validate(instance=json.loads(json_data), schema=json.loads(json_schema))

    except Exception as e:
        print(str(e))
        return False
    
    print("validation successful")
    return True


# collection stuff
def get_collection_abi():
    with open("contracts/collectionContract.json") as f:
        info_json = json.load(f)
    abi = info_json
    return abi

def get_collection_bytecode():
    with open("contracts/collectionContract.bin", "r") as f:
        info_bytecode = f.read()
    return info_bytecode


def get_collection_metadata_schema():
    with open("collection_schema.json") as f:
        info_json = f.read()
    return info_json



def getCollectionSchema():

    # define collection schema
    collectionSchemaJson = get_collection_metadata_schema()

    #print("Collection Metadata Schema")
    #print("------------------------------------")
    #print(collectionSchemaJson)
    #print("------------------------------------")

    return collectionSchemaJson



# item stuff
def get_item_abi():
    with open("contracts/itemContract.json") as f:
        info_json = json.load(f)
    abi = info_json
    return abi

def get_item_bytecode():
    with open("contracts/itemContract.bin", "r") as f:
        info_bytecode = f.read()
    return info_bytecode


def get_item_metadata_schema():
    with open("item_schema.json") as f:
        info_json = f.read()
    return info_json

def getItemSchema():

    # define item nft schema
    itemSchema = ItemMetadataSchema()
    itemSchemaJson = itemSchema.toJSON()

    #print("Item NFT Schema ")
    #print("------------------------------------")
    #print(itemSchemaJson)
    #print("------------------------------------")

    return itemSchemaJson





# OGC Collection Metadata Generation
def getFeatureCollectionMetadata(collection, collectionSchemaJson):

    print("Build Collection Metadata")

    id = collection.get("id")
    title = collection.get("title")
    description = collection.get("description")
    itemType = collection.get("itemType")

    attributeTypes = []
    if title.lower() == "dcl halloween 2019":
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="body_shapes",
                    display_name="body_shapes",
                    struct_type="list",
                    scalar_type="string",
                    list = ["base male", "base female"]))
        
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="category",
                    display_name="category",
                    struct_type="list",
                    scalar_type="string",
                    list = ["Helmet", "Hat"]))
            
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="collection",
                    display_name="collection",
                    struct_type="list",
                    scalar_type="string",
                    list = ["Halloween 2019"]))
        
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="rarity",
                    display_name="rarity",
                    struct_type="list",
                    scalar_type="string",
                    list = ["rare"]))
        
        
        
    if title.lower() == "decentraland":
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="type",
                    display_name="type",
                    struct_type="list",
                    scalar_type="string",
                    list = ["parcel", "estate"]))
        
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="status",
                    display_name="status",
                    struct_type="list",
                    scalar_type="string",
                    list = ["buy", "rent"]))
            
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="x",
                    display_name="x",
                    struct_type="scalar",
                    scalar_type="integer",
                    min=-200,
                    max=200))
        
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="y",
                    display_name = "y",
                    struct_type="scalar",
                    scalar_type="integer",
                    min=-200,
                    max=200))
        
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="adjacent-to-road",
                    display_name = "adjacent to road",
                    struct_type="scalar",
                    scalar_type="boolean"))
        
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="near-a-district",
                    display_name = "near a district",
                    struct_type="scalar",
                    scalar_type="boolean"))
        
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="distance-to-road",
                    display_name = "distance to road",
                    struct_type="scalar",
                    scalar_type="integer",
                    min = 0,
                    max = 10))
        
        attributeTypes.append(
                AttributeTypeMetadata(
                    name="distance-to-district",
                    display_name = "distance to district",
                    struct_type="scalar",
                    scalar_type="integer",
                    min = 0,
                    max = 10))
    

    print("create collection metadata")
    collectionMetadata = CollectionMetadata(name=title, type=itemType, description=description, attribute_types=attributeTypes)
    collectionMetadataJson = collectionMetadata.toJSON()

    print("Collection Metadata")
    print("------------------------------------")
    print(collectionMetadataJson)
    print("------------------------------------")

    #validate metadata
    print("validate schema")
    validate_json(collectionMetadataJson, collectionSchemaJson)
    print("schema validated ")

    return collectionMetadataJson






# OGC Item Feature Metadata Generation
def getFeatureItemMetadata(feature, itemSchemaJson: str):

    properties = feature['properties']
    #print(json.dumps(properties, indent=4))

    name = properties.get("name")
                

    attributes = []
    '''
    for trait in openSeaAsset.traits:
        print("------------------ trait: " + str(trait))

        display_type = "checkbox"
        if trait.display_type == "number":
            display_type = "number"

        assetMetadata = AssetAttributeMetadata(
                id = str(tokenId) + "-" + trait.trait_type,
                type = trait.trait_type,
                display_name = str(trait.value),
                display_type = display_type,
                value = trait.value)

        # decentraland trait normalization

        if trait.trait_type.lower() == "distance to district":

            assetMetadata.id = str(tokenId) + "-distance-to-district"
            assetMetadata.type = "distance-to-district"
            assetMetadata.display_name = str(trait.value)
            assetMetadata.display_type = "number"

            # add another trait based on the distance
            if assetMetadata.value < 3:
                adjacentAttribute = AssetAttributeMetadata(
                    id = str(tokenId) + "-" + "near-a-district",
                    type = "near-a-district",
                    display_name = "yes",
                    display_type = "boolean",
                    value = True)
                
                attributes.append(adjacentAttribute)

        if trait.trait_type.lower() == "distance to road":

            assetMetadata.id = str(tokenId) + "-distance-to-road"
            assetMetadata.type = "distance-to-road"
            assetMetadata.display_name = str(trait.value)
            assetMetadata.display_type = "number"

            # add another trait based on the distance
            if assetMetadata.value < 3:
                adjacentAttribute = AssetAttributeMetadata(
                    id = str(tokenId) + "-" + "adjacent-to-road",
                    type = "adjacent-to-road",
                    display_name = "yes",
                    display_type = "boolean",
                    value = True)
                attributes.append(adjacentAttribute)


        if trait.trait_type.lower() == "type":
            if trait.value.lower() == "land":
                assetMetadata.display_name = "parcel"
                assetMetadata.value = "parcel"

        attributes.append(assetMetadata)
    '''

    itemMetadata = ItemMetadata(
        name = name,  
        display_name = name,  
        attributes = attributes)

    itemMetadataJson = itemMetadata.toJSON()
    print("Feature Metadata")
    print("------------------------------------")
    print(itemMetadataJson)
    print("------------------------------------")

    #validate metadata
    #print("validate schema")
    validate_json(itemMetadataJson, itemSchemaJson)
    #print("schema validated ")

    return itemMetadataJson



def constructCollectionFactory(w3, name, symbol):

    # construct a new collection contract that will be used to create these collection NFT's
    collectionABI = get_collection_abi()
    collectionBytecode = get_collection_bytecode()

    ownerPrivateKey = os.environ.get('ETHEREUM_PRIVATE_KEY')
    ownerPublicAddress = os.environ.get('ETHEREUM_PUBLIC_ADDRESS')

    collectionContract = w3.eth.contract(abi=collectionABI, bytecode=collectionBytecode)
    collection_txn = collectionContract.constructor(name, symbol).build_transaction(
        {
            'from': ownerPublicAddress,
            'nonce': w3.eth.get_transaction_count(ownerPublicAddress),
        }
    )

    #print("create collection contract: " + name + ", symbol: " + symbol)
    tx_create = w3.eth.account.sign_transaction(collection_txn, ownerPrivateKey)
    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    collectionContract = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=collectionABI
    )

    print("xxxxxxxxxxxxxxxxxxxxxxxxx  collection contract: " + tx_receipt.contractAddress)

    return collectionContract

def constructItemFactory(w3, name, symbol):

    # construct a new item contract that will be used to create these item NFT's
    itemABI = get_item_abi()
    itemBytecode = get_item_bytecode()

    ownerPrivateKey = os.environ.get('ETHEREUM_PRIVATE_KEY')
    ownerPublicAddress = os.environ.get('ETHEREUM_PUBLIC_ADDRESS')

    itemContract = w3.eth.contract(abi=itemABI, bytecode=itemBytecode)
    item_txn = itemContract.constructor(name, symbol).build_transaction(
        {
            'from': ownerPublicAddress,
            'nonce': w3.eth.get_transaction_count(ownerPublicAddress),
        }
    )

    #print("create item contract: " + name + ", symbol: " + symbol)
    tx_create = w3.eth.account.sign_transaction(item_txn, ownerPrivateKey)
    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    itemContract = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=itemABI
    )

    print("xxxxxxxxxxxxxxxxxxxxxxxxx  item contract: " + tx_receipt.contractAddress)

    return itemContract

def retrieve_ogc_collection(collection_slug):

    print("connect to Web3")
    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    print("connect to IPFS")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    ownerPrivateKey = os.environ.get('ETHEREUM_PRIVATE_KEY')
    ownerPublicAddress = os.environ.get('ETHEREUM_PUBLIC_ADDRESS')

    print("(Rich) construct collection factory ")
    collectionFactory = constructCollectionFactory(w3, "OGC Collection", "OGCC")

    print("(Rich) construct item factory ")
    featureFactory = constructItemFactory(w3, "OGC Item", "OGCI")
    

    


    # get opensea collections dictionary
    print("Get OGC Collection collection data")

    feature_dataset = OGCFeature('http://localhost:5021/')

    data = feature_dataset.collections() 
    collections = data.get("collections")

    for collection in collections:

        print("-------------------------------")
        id = collection.get("id")
        title = collection.get("title")
        description = collection.get("description")
        itemType = collection.get("itemType")

        print ("collection(" + id + "): " + title)

        if collection_slug == id and itemType == "feature":

            print("construct collection: " + title)
            collectionSchema = getCollectionSchema()
            collectionMetadata = getFeatureCollectionMetadata(collection, collectionSchema)
            collectionMetadataHash = ipfsclient.add_str(collectionMetadata)

            collectionUri = "ipfs://" + collectionMetadataHash

            nonce1 = w3.eth.get_transaction_count(ownerPublicAddress) 
            transaction = collectionFactory.functions.mint(collectionUri).build_transaction({
                    'from': ownerPublicAddress,
                    'gas' : 8000000,
                    'nonce': nonce1,
                })
            signed_tx = w3.eth.account.sign_transaction(transaction, ownerPrivateKey)
            txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

            vals = array.array('B', txn_receipt1.logs[0].topics[3])
            collectionNFTTokenId = vals[len(vals) - 1]

            print("collection token id: " + str(collectionNFTTokenId))


            query_url = "http://localhost:5021/collections/" + id + "/items?limit=100"
            response = requests.get(query_url)
            data = response.json()

            #print("collection data: " + str(data))

            i = 0
            for feature in data["features"]:


                featureSchema = getItemSchema()
                featureMetadata = getFeatureItemMetadata(feature, featureSchema)
                featureMetadataHash = ipfsclient.add_str(featureMetadata)

                itemUri = "ipfs://" + featureMetadataHash

                nonce1 = w3.eth.get_transaction_count(ownerPublicAddress) 
                transaction = featureFactory.functions.mint(itemUri).build_transaction({
                        'from': ownerPublicAddress,
                        'gas' : 8000000,
                        'nonce': nonce1,
                    })
                signed_tx = w3.eth.account.sign_transaction(transaction, ownerPrivateKey)
                txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                featureNFTReceipt = w3.eth.wait_for_transaction_receipt(txn_hash1)

                vals = array.array('B', featureNFTReceipt.logs[0].topics[3])
                featureNFTTokenId = vals[len(vals) - 1]


                print("add child token to parent")
                print("owner add: " + ownerPublicAddress)
                print("feature contract add: " + featureFactory.address)
                print("feature token id: " + str(featureNFTTokenId))
                print("collection token id: " + str(collectionNFTTokenId))

                # add child feature to parent collection
                nonce1 = w3.eth.get_transaction_count(ownerPublicAddress) 
                transaction = featureFactory.functions.nestTransferFrom(
                    ownerPublicAddress,
                    collectionFactory.address,
                    featureNFTTokenId,
                    collectionNFTTokenId,
                    "0x0000000000000000000000000000000000000000000000000000000000000000"
                ).build_transaction({
                        'from': ownerPublicAddress,
                        'gas' : 8000000,
                        'nonce': nonce1,
                    })
                signed_tx = w3.eth.account.sign_transaction(transaction, ownerPrivateKey)
                txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

                print("accept child token addition")

                # accept child to parent
                nonce1 = w3.eth.get_transaction_count(ownerPublicAddress) 
                transaction = collectionFactory.functions.acceptChild(
                    collectionNFTTokenId,
                    0,
                    featureFactory.address,
                    featureNFTTokenId
                ).build_transaction({
                        'from': ownerPublicAddress,
                        'gas' : 8000000,
                        'nonce': nonce1,
                    })
                signed_tx = w3.eth.account.sign_transaction(transaction, ownerPrivateKey)
                txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

                print("done adding child")

        
def synch_feature_list(current_page, page_size, search, sort, **kwargs):

    #retrieve_ogc_collection("decentraland")

    print("(Rich) sync lakes ")
    retrieve_ogc_collection("lakes")
    


    #print("(Rich) return features:  " + str(p))
    p = []
    total_count = 0

    return p, total_count
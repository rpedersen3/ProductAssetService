import graphene
from graphene import ObjectType
from graphene.types import generic

from web3 import Web3
from web3.middleware import geth_poa_middleware

import ipfshttpclient

import os

import json
import jsonschema
from jsonschema import validate

from api_attribute import AttributeType
from api_collection import Collection, CollectionFilterInput, CollectionList, Collections, CollectionSortInput

from constants import CollectionInterfaceId, ItemInterfaceId


import redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

import logging
logger = logging.getLogger(__name__)






def parse_attribute_types(collection, metaAttributeTypes):
    collection.attribute_types = []
    if metaAttributeTypes != None:
        for metaAttributeType in metaAttributeTypes:

            attributeType = AttributeType()
            attributeType.id = metaAttributeType.get("name")
            attributeType.name = metaAttributeType.get("name")
            attributeType.display_name = metaAttributeType.get("display_name")
            attributeType.struct_type = metaAttributeType.get("struct_type")
            attributeType.scalar_type = metaAttributeType.get("scalar_type")
            attributeType.min = metaAttributeType.get("min")
            attributeType.max = metaAttributeType.get("max")

            if attributeType.struct_type == 'scalar' and attributeType.scalar_type == "integer":
                attributeType.display_type = 'number'

            if attributeType.struct_type == 'scalar' and attributeType.scalar_type == "boolean":
                attributeType.display_type = 'checkbox-list'
                attributeType.values = []
                attributeType.values.append("true")
                attributeType.values.append("false")

            if attributeType.struct_type == 'list':
                attributeType.display_type = 'checkbox-list'
                

            metaList = metaAttributeType.get("list")
            if (metaList != None):
                attributeType.values = []
                for metaListItem in metaList:
                    attributeType.values.append(metaListItem)

            collection.attribute_types.append(attributeType)

def get_collection_contract(w3, collectionContractAddress):

    with open("contracts/collectionContract.json") as f:
        info_json = json.load(f)
    collectionABI = info_json
    collectionFactoryContract = w3.eth.contract(address=collectionContractAddress, 
                                        abi=collectionABI)
    
    supportsCollection = collectionFactoryContract.functions.supportsInterface(CollectionInterfaceId).call()
    print("collection supports interface: " + str(collectionContractAddress) + " supports: " + str(supportsCollection))


    if supportsCollection == False:
        return None
    
    return collectionFactoryContract


def retrieve_collection(filter):

    print("connect to blockchain on http://localhost:8546")

    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    print("connect to ipfs on /ip4/127.0.0.1/tcp/5001")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    collectionContractAddress = os.environ.get('FEATURE_COLLECTION_CONTRACT')
    collectionTokenId = 1

    # get list of items
    collectionNFTs = []
    if filter != None and filter.collection_token_id != None and filter.collection_address:
        # get list from collection
        print("(Rich) ************* filter items by collection address: " + filter.collection_address)
        collectionContractAddress = filter.collection_address
        collectionTokenId = int(filter.collection_token_id)

    collectionContract = get_collection_contract(w3, collectionContractAddress) 

    print("top collection: " + str(collectionContractAddress)) 

    tokenURI = collectionContract.functions.tokenURI(collectionTokenId).call()

    print("retrieve collection metadata")
    cid = tokenURI.replace("ipfs://", "");
    metadataJson = ipfsclient.cat(cid)

    #print("l0 ipfs data: " + str(metadataJson))
    
    metaCollection = json.loads(metadataJson)
    collection = Collection()
    collection.id = collectionContractAddress + "-" + str(collectionTokenId)
    collection.name = metaCollection.get("name")
    collection.image = metaCollection.get("image")
    collection.slug = "/collection/" + str(collectionTokenId)
    collection.childs = []

    parse_attribute_types(collection, metaCollection.get("attribute_types"))


    childCollectionTokenIds = collectionContract.functions.childrenOf(collectionTokenId).call()
    for childCollectionTokenId in childCollectionTokenIds:
        childTokenId = childCollectionTokenId[0]
        childAddress = childCollectionTokenId[1]

        print("childAddress: " + str(childAddress))

        childCollectionContract = get_collection_contract(w3, childAddress)
        if childCollectionContract != None:

            childTokenURI = childCollectionContract.functions.tokenURI(childTokenId).call()

            cid = childTokenURI.replace("ipfs://", "");
            metadataJson = ipfsclient.cat(cid)
            
            metaCollection = json.loads(metadataJson)

            #print("l1 ipfs data: " + str(metadataJson))

            childCollection = Collection()
            childCollection.id = str(childTokenId)
            childCollection.name = metaCollection.get("name")
            childCollection.image = metaCollection.get("image")
            childCollection.slug = "/collection/" + str(childTokenId)
            childCollection.childs = []

            parse_attribute_types(childCollection, metaCollection.get("attribute_types"))

            collection.childs.append(childCollection)

            level2Collections = childCollectionContract.functions.childrenOf(childTokenId).call()

            for level2Collection in level2Collections:
                level2TokenId = level2Collection[0]
                level2ContractAddress = level2Collection[1]

                level2CollectionContract = get_collection_contract(w3, level2ContractAddress)
                if level2CollectionContract != None:

                    level2TokenURI = level2CollectionContract.functions.tokenURI(level2TokenId).call()
                    cid = level2TokenURI.replace("ipfs://", "");
                    metadataJson = ipfsclient.cat(cid)
                    
                    metaCollection = json.loads(metadataJson)

                    #print("l2 ipfs data: " + str(metadataJson))

                    level2Collection = Collection()
                    level2Collection.id = str(level2TokenId)
                    level2Collection.name = metaCollection.get("name")
                    level2Collection.image = metaCollection.get("image")
                    level2Collection.slug = "/collection/" + str(level2TokenId)
                    level2Collection.childs = []

                    print("parse attribute types")
                    parse_attribute_types(level2Collection, metaCollection.get("attribute_types"))

                    print("append")
                    childCollection.childs.append(level2Collection)

                    print("append done")
    
    print("return collection")
    return collection

class CollectionQuery(graphene.ObjectType):

    collection = graphene.Field(
        Collection,
        id=graphene.Int(default_value=None),
        slug=graphene.String(default_value=None)
    )
    
    collections = graphene.Field(
        Collections,
        filter=graphene.Argument(CollectionFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(CollectionSortInput, default_value={})
    )
    

    
    '''
    @staticmethod
    def resolve_collection(self, info, id=None, slug=None):

        print("**************  get collection: " + str(id) + " slug: " + str(slug))
        return retrieve_collection(slug)
    '''
    
    @staticmethod
    def resolve_collections(self, info, filter, current_page, page_size, search, sort):


        total_count = 4

        topCollection = retrieve_collection(filter)
        collections = topCollection.childs
        #print("return the children: " + str(collections))

        return CollectionList(collections=collections, total_count=total_count)
    
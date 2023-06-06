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




import redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

import logging
logger = logging.getLogger(__name__)




def parse_products(collection, metaProducts):

    collection.products = []
    if metaProducts != None:
        for metaProduct in metaProducts:

            print("++++++++++ add product to collection: " + metaProduct.get("name"))

            product = Product()
            product.id = metaProduct.get("id")
            product.name = metaProduct.get("name")

            collection.products.append(product)


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


def retrieve_collection(slug):

    print("connect to blockchain on http://localhost:8546")

    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    print("connect to ipfs on /ip4/127.0.0.1/tcp/5001")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    nftContractAddress = os.environ.get('FEATURE_COLLECTION_CONTRACT')

    print("retrieve collection contract")
    with open("contracts/collectionContract.json") as f:
        info_json = json.load(f)
    catABI = info_json["abi"]

    collectionContract = w3.eth.contract(address=nftContractAddress, 
                                    abi=catABI)

    tokenId = int(slug.replace("/collection/", ""));

    tokenURI = collectionContract.functions.tokenURI(tokenId).call()

    print("retrieve collection metadata")
    cid = tokenURI.replace("ipfs://", "");
    metadataJson = ipfsclient.cat(cid)

    #print("l0 ipfs data: " + str(metadataJson))
    
    metaCollection = json.loads(metadataJson)
    collection = Collection()
    collection.id = str(tokenId)
    collection.name = metaCollection.get("display_name")
    collection.image = metaCollection.get("image")
    collection.slug = "/collection/" + str(tokenId)
    collection.childs = []

    parse_products(collection, metaCollection.get("products"))
    parse_attribute_types(collection, metaCollection.get("attribute_types"))


    childCollectionTokenIds = collectionContract.functions.childrenOf(tokenId).call()
    for childCollectionTokenId in childCollectionTokenIds:
        childTokenId = childCollectionTokenId[0]
        #contractAddress = childCollection[1]

        childTokenURI = collectionContract.functions.tokenURI(childTokenId).call()

        cid = childTokenURI.replace("ipfs://", "");
        metadataJson = ipfsclient.cat(cid)
        
        metaCollection = json.loads(metadataJson)

        #print("l1 ipfs data: " + str(metadataJson))

        childCollection = Collection()
        childCollection.id = str(childTokenId)
        childCollection.name = metaCollection.get("display_name")
        childCollection.image = metaCollection.get("image")
        childCollection.slug = "/collection/" + str(childTokenId)
        childCollection.childs = []

        parse_products(childCollection, metaCollection.get("products"))
        parse_attribute_types(childCollection, metaCollection.get("attribute_types"))

        collection.childs.append(childCollection)

        level2Collections = collectionContract.functions.childrenOf(childTokenId).call()

        for level2Collection in level2Collections:
            level2TokenId = level2Collection[0]
            #contractAddress = topCollection[1]

            level2TokenURI = collectionContract.functions.tokenURI(level2TokenId).call()
            cid = level2TokenURI.replace("ipfs://", "");
            metadataJson = ipfsclient.cat(cid)
            
            metaCollection = json.loads(metadataJson)

            #print("l2 ipfs data: " + str(metadataJson))

            level2Collection = Collection()
            level2Collection.id = str(level2TokenId)
            level2Collection.name = metaCollection.get("display_name")
            level2Collection.image = metaCollection.get("image")
            level2Collection.slug = "/collection/" + str(level2TokenId)
            level2Collection.childs = []

            parse_products(level2Collection, metaCollection.get("products"))
            parse_attribute_types(level2Collection, metaCollection.get("attribute_types"))

            childCollection.childs.append(level2Collection)
    
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
    

    
    
    @staticmethod
    def resolve_collection(self, info, id=None, slug=None):

        print("**************  get collection: " + str(id) + " slug: " + str(slug))
        return retrieve_collection(slug)
    
    
    @staticmethod
    def resolve_collections(self, info, filter, current_page, page_size, search, sort):

        topCollectionSlug = "/collection/1"
        if filter != None and filter.slug != None:
            topCollectionSlug = filter.slug

        total_count = 4

        print("get collections for this top slug: " + topCollectionSlug)
        topCollection = retrieve_collection(topCollectionSlug)
        collections = topCollection.childs
        print("return the children: " + str(collections))

        return CollectionList(collections=collections, total_count=total_count)
    
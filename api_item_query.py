import graphene
from graphene import ObjectType
from graphene.types import generic

import ipfshttpclient

import os

import json
import jsonschema
from jsonschema import validate



from web3 import Web3
from web3.middleware import geth_poa_middleware


from api_attribute import Attribute, AttributeValue
from api_item import Item, ItemFilterInput, ItemList, Items, ItemSortInput
from api_collection import Collection, Collections

from constants import CollectionInterfaceId, ItemInterfaceId

import redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

import logging
logger = logging.getLogger(__name__)

def get_schema():
    with open('nftschema.json', 'r') as file:
        schema = json.load(file)
    return schema

def get_example_json():
    with open('example2.json', 'r') as file:
        data = json.load(file)
    return data

def validate_json(json_data):
    """REF: https://json-schema.org/ """
    # Describe what kind of json you expect.
    execute_api_schema = get_schema()
    try:
        validate(instance=json_data, schema=execute_api_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        err = "************************** Given JSON data is InValid"
        return False, err
    message = "*************************Given JSON data is Valid"
    return True, message

def get_collection_contract(w3, collectionContractAddress):

    with open("contracts/collectionContract.json") as f:
        info_json = json.load(f)
    collectionABI = info_json
    collectionFactoryContract = w3.eth.contract(address=collectionContractAddress, 
                                        abi=collectionABI)
    
    supportsCollection = collectionFactoryContract.functions.supportsInterface(CollectionInterfaceId).call()
    if supportsCollection == False:
        return None
    
    return collectionFactoryContract

def get_item_contract(w3, itemContractAddress):

    with open("contracts/itemContract.json") as f:
        info_json = json.load(f)
    itemABI = info_json
    itemFactoryContract = w3.eth.contract(address=itemContractAddress, 
                                        abi=itemABI)
    
    supportsCollection = itemFactoryContract.functions.supportsInterface(ItemInterfaceId).call()
    if supportsCollection == False:
        return None
    
    return itemFactoryContract

   
def add_collection(collections, contractAddress, tokenId, collectionMetadata):

    if collectionMetadata != None:
        collection = Collection()
        collection.id = str(contractAddress) + "-" + str(tokenId)
        collection.name = collectionMetadata.get("name")

        collections.append(collection)

    return collections

def retrieve_collections(w3, topAddress, topTokenId):

    collections = []

    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    print("get contract")
    topCollectionFactoryContract = get_collection_contract(w3, topAddress)
    tokenURI = topCollectionFactoryContract.functions.tokenURI(topTokenId).call()

    cid = tokenURI.replace("ipfs://", "");
    metadataJson = ipfsclient.cat(cid)

    print("metdata: " + str(metadataJson))
    collectionMetadata = json.loads(metadataJson)
    add_collection(collections, topAddress, topTokenId, collectionMetadata)

    print("get children ")
    childCollectionTokenIds = topCollectionFactoryContract.functions.childrenOf(topTokenId).call()
    for childCollectionTokenId in childCollectionTokenIds:

        print("got child: " + str(childCollectionTokenId))
        childTokenId = childCollectionTokenId[0]
        childContractAddress = childCollectionTokenId[1]
        collectionFactoryContract = get_collection_contract(w3, childContractAddress)
        if collectionFactoryContract != None:

            childTokenURI = collectionFactoryContract.functions.tokenURI(childTokenId).call()

            cid = childTokenURI.replace("ipfs://", "");
            metadataJson = ipfsclient.cat(cid)
            
            collectionMetadata = json.loads(metadataJson)
            add_collection(collections, childContractAddress, childTokenId, collectionMetadata)

            level2Collections = collectionFactoryContract.functions.childrenOf(childTokenId).call()

            for level2Collection in level2Collections:
                level2TokenId = level2Collection[0]
                level2ContractAddress = level2Collection[1]

                level2CollectionFactoryContract = get_collection_contract(w3, level2ContractAddress)
                if level2CollectionFactoryContract != None:

                    level2TokenURI = level2CollectionFactoryContract.functions.tokenURI(level2TokenId).call()
                    cid = level2TokenURI.replace("ipfs://", "");
                    metadataJson = ipfsclient.cat(cid)
                    
                    collectionMetadata = json.loads(metadataJson)
                    add_collection(collections, level2ContractAddress, level2TokenId, collectionMetadata)         
    
    return collections

class ItemQuery(graphene.ObjectType):
    item = graphene.Field(
        Item,
        id=graphene.String(default_value=None),
        slug=graphene.String(default_value=None),
        barcode=graphene.String(default_value=None),
    )
    items = graphene.Field(
        Items,
        filter=graphene.Argument(ItemFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(ItemSortInput, default_value={})
    )
    

    
    @staticmethod
    def resolve_item(self, info, id=None, slug=None, barcode=None):
        print("************ not implemented ************")
        '''
        if id:
            print("(Rich) resolve item for id: " + str(id))
            #product = Product.search([('id', '=', id)], limit=1)
        elif slug:
            slug = slug.replace("/product-asset/", "")
            print("(Rich) resolve item for slug: " + str(slug))
            ids = slug.split("-")
            productId = ids[len(ids)-2]
            assetId = ids[len(ids)-1]
            #print("(Rich) resolve item for id from slug: " + str(assetId))
            #product = Product.search([('website_slug', '=', slug)], limit=1)
        elif barcode:
            print("(Rich) resolve item for barcode: " + str(barcode))
            #product = Product.search([('barcode', '=', barcode)], limit=1)
        else:
            print("(Rich) resolve item not defined ")
            #product = Product

        w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

        nftContractAddress = productId
        tokenId = int(assetId)
        erc721Contract = w3.eth.contract(address=nftContractAddress, 
                                        abi=erc721ABI)

        totalSupply = erc721Contract.functions.totalSupply().call()
        contractName = erc721Contract.functions.name().call()
        contractSymbol = erc721Contract.functions.symbol().call()

        tokenURI = erc721Contract.functions.tokenURI(int(assetId)).call()
        #print("token(" + str(tokenId) + ") uri: " + str(tokenURI))

        cid = tokenURI.replace("ipfs://", "");
        metadataJson = ipfsclient.cat(cid)
        
        metaAsset = json.loads(metadataJson)

        #print("ipfs data: " + str(metadataJson))

        item = Item()
        item.id = str(tokenId)
        #item.product = product
        item.tokenId = tokenId
        item.name = metaAsset.get("name")
        item.display_name = metaAsset.get("display_name")
        #item.description = assetMetadata["description"]
        item.image = metaAsset.get("image")
        item.slug = "/product-asset/" + nftContractAddress + "-" + str(tokenId)
        item.attribute_values = []

        metaAttributes = metaAsset.get("attributes")
        for metaAttribute in metaAttributes:

            #print("meta attribute: " + str(metaAttribute))

            attributeValue = AttributeValue()
            attributeValue.id = metaAttribute.get("id")
            attributeValue.type = metaAttribute.get("type")
            attributeValue.display_type = metaAttribute.get("display_type")
            attributeValue.display_name = metaAttribute.get("display_name")
            attributeValue.value = metaAttribute.get("value")


            #print("product asset =>  attribute values : " + str(attributeValue))
            item.attribute_values.append(attributeValue)


        print("(Rich) product asset found: " + str(item))
        return item
        '''
        return

    @staticmethod
    def resolve_items(self, info, filter, current_page, page_size, search, sort):
        print("(Rich) resolve_items => get items: ")
        if filter != None:
            print("   filter: " + str(filter))

        items, total_count, attribute_values, min_price, max_price = get_item_list(
            current_page, page_size, search, sort, filter)
        
        #print("(Rich) resolve_items => get items return list: ")
        return ItemList(items=items, total_count=total_count, attribute_values=attribute_values,
                    min_price=min_price, max_price=max_price)
    

    
def get_item_list(current_page, page_size, search, sort, filter: ItemFilterInput):

    #print("connect to Web3")
    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    collectionNFTs = []

    # get list of items
    collectionNFTs = []
    if filter.collection_token_id != None and filter.collection_address:
        # get list from collection
        print("(Rich) ************* filter items by collection address: " + filter.collection_address)
        collectionNFTs = retrieve_collections(w3, filter.collection_address, filter.collection_token_id)
        
    print("(Rich) get items for collections: " + str(collectionNFTs))



    total_count = 0
    p = []
    attribute_values = []

 
    #print("connect to IPFS")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    
    
    for collectionNFT in collectionNFTs:

        # childrenNFTId is contractAddress - tokenId

        ids = collectionNFT.id.split("-")
        collectionContractAddress = ids[len(ids)-2]
        collectionTokenId = int(ids[len(ids)-1])

        collectionFactoryContract = get_collection_contract(w3, collectionContractAddress)

        childIds = collectionFactoryContract.functions.childrenOf(collectionTokenId).call()

        print("childsIds: " + str(childIds))
        for childId in childIds:

            childTokenId = childId[0]
            childContractAddress = childId[1]

            print("get item contract: " + str(childContractAddress))
            itemContractFactory = get_item_contract(w3, childContractAddress)
            if itemContractFactory != None:

                tokenURI = itemContractFactory.functions.tokenURI(childTokenId).call()
                cid = tokenURI.replace("ipfs://", "");
                metadataJson = ipfsclient.cat(cid)
                
                itemMetadata = json.loads(metadataJson)

                print("ipfs data: " + str(metadataJson))

                item = Item()
                item.id = str(childContractAddress) + "-" + str(childTokenId)
                item.tokenId = childTokenId
                item.name = itemMetadata.get("name")
                item.display_name = itemMetadata.get("display_name")

                item.description = itemMetadata.get("description")
                item.image = itemMetadata.get("image")
                #item.slug = "/product-asset/" + nftContractAddress + "-" + str(tokenId)
                item.attribute_values = []

                metaAttributes = itemMetadata.get("attributes")
                if metaAttributes != None:
                    for metaAttribute in metaAttributes:

                        print("meta attribute: " + str(metaAttribute))

                        attributeValue = AttributeValue()
                        attributeValue.id = metaAttribute.get("id")
                        attributeValue.type = metaAttribute.get("type")
                        attributeValue.display_type = metaAttribute.get("display_type")
                        attributeValue.display_name = metaAttribute.get("display_name")
                        attributeValue.value = metaAttribute.get("value")

                        #display_type = "checkbox"
                        #if (metaAttribute.get("display_type") == "number"):
                        #    display_type = "number"
                        #attributeValue.display_type = display_type

                        attributeFilter = None
                        if filter != None and filter.range_filters != None:
                            
                            for range_filter in filter.range_filters: 
                                if range_filter.name.lower() == metaAttribute.get("type").lower():
                                    attributeFilter = range_filter

                        
                        if attributeFilter:
                            if int(attributeValue.value) < int(attributeFilter.min) or int(attributeValue.value) > int(attributeFilter.max):
                                filterAsset = False
                                #print("(Rich) ************  not pass filter: " + attributeFilter.name)

                        print("item asset =>  attribute values : " + str(attributeValue))
                        item.attribute_values.append(attributeValue)


                #print('append item asset: ' + str(item))
                total_count += 1

                p.append(item)
 

    #print("(Rich) return item assets:  " + str(p))
    return p, total_count, attribute_values, 0.0, 0.0


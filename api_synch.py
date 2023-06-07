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

import ipfshttpclient

from helper import FilterVisibility, SortEnum

from api_category import Categories, Category

from api_item import Items, Item
from api_collection import Collections, Collection

from collection_metadata_schema import CollectionMetadataSchema
from collection_metadata import CollectionMetadata

from item_metadata_schema import ItemMetadataSchema
from item_metadata import ItemMetadata

from attribute_type_metadata import AttributeTypeMetadata
from attribute_metadata import AttributeMetadata

from opensea_decentraland_asset import OpenSeaAsset

from constants import CollectionInterfaceId, ItemInterfaceId

from web3.gas_strategies.rpc import rpc_gas_price_strategy


import redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

from opensea import OpenseaAPI

import logging
logger = logging.getLogger(__name__)



class SynchAssets(graphene.Interface):

    items = graphene.List(Item)
    total_count = graphene.Int(required=True)

class SynchAssetList(graphene.ObjectType):
    class Meta:
        interfaces = (Items,)


class SynchCategories(graphene.Interface):

    Collections = graphene.List(Category)
    total_count = graphene.Int(required=True)

class SynchCategoryList(graphene.ObjectType):
    class Meta:
        interfaces = (Collections,)



class SynchFilterInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int)
    category_id = graphene.List(graphene.Int)
    category_slug = graphene.String()
    # Deprecated
    attribute_value_id = graphene.List(graphene.Int)
    attrib_values = graphene.List(graphene.String)
    name = graphene.String()
    min_price = graphene.Float()
    max_price = graphene.Float()
    min_number_of_assets = graphene.Int()


class SynchSortInput(graphene.InputObjectType):
    id = SortEnum()
    name = SortEnum()
    price = SortEnum()


class SynchQuery(graphene.ObjectType):

    synch_assets = graphene.Field(
        Items,
        filter=graphene.Argument(SynchFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(SynchSortInput, default_value={})
    )

    synch_categories = graphene.Field(
        Collections,
        filter=graphene.Argument(SynchFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(SynchSortInput, default_value={})
    )
    
    @staticmethod
    def resolve_synch_assets(self, info, filter, current_page, page_size, search, sort):
        #print("(Rich) resolve_synch_assets => get assets: ")
        items, total_count = synch_asset_list(
            current_page, page_size, search, sort, **filter)
        
        #print("(Rich) resolve_assets => get assets return list: ")
        return SynchAssetList(items=items, total_count=total_count)
    
    @staticmethod
    def resolve_synch_categories(self, info, filter, current_page, page_size, search, sort):
        #print("(Rich) resolve_synch_categories => get categories: ")
        collections, total_count = synch_category_list(
            current_page, page_size, search, sort, **filter)
        
        return SynchCategoryList(collections=collections, total_count=total_count)

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



def get_collection_abi():
    with open("contracts/collectionContract.json") as f:
        info_json = json.load(f)
    abi = info_json
    return abi

def get_collection_bytecode():
    with open("contracts/collectionContract.bin", "r") as f:
        info_bytecode = f.read()
    return info_bytecode


def validate_json(json_data, json_schema):

    try:
        validate(instance=json.loads(json_data), schema=json.loads(json_schema))

    except Exception as e:
        print(str(e))
        return False
    
    #print("validation successful")
    return True



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

def getCollectionSchema():

    # define decentraland nft schema
    collectionSchema = CollectionMetadataSchema()
    collectionSchemaJson = collectionSchema.toJSON()

    #print("NFT Collection Schema ")
    #print("------------------------------------")
    #print(collectionSchemaJson)
    #print("------------------------------------")

    return collectionSchemaJson



def getItemSchema():

    # define asset nft schema
    itemSchema = ItemMetadataSchema()
    itemSchemaJson = itemSchema.toJSON()

    #print("NFT Item Schema ")
    #print("------------------------------------")
    #print(itemSchemaJson)
    #print("------------------------------------")

    return itemSchemaJson


def getAssetMetadata(tokenId: int, openSeaAsset: OpenSeaAsset, assetSchemaJson: str):

    attributes = []
    
    for trait in openSeaAsset.traits:
        print("------------------ trait: " + str(trait))

        display_type = "checkbox"
        if trait.display_type == "number":
            display_type = "number"

        assetMetadata = AttributeMetadata(
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
                adjacentAttribute = AttributeMetadata(
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
                adjacentAttribute = AttributeMetadata(
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

    assetMetadata = ItemMetadata(
        name = openSeaAsset.name,  
        display_name = openSeaAsset.name,  
        image = openSeaAsset.image_url,
        description="", 
        #price = 87.5,
        attributes = attributes)

    assetMetadataJson = assetMetadata.toJSON()
    #print("Decentraland Asset Metadata")
    #print("------------------------------------")
    #print(assetMetadataJson)
    #print("------------------------------------")

    #validate metadata
    #print("validate schema")
    validate_json(assetMetadataJson, assetSchemaJson)
    #print("schema validated ")

    return assetMetadataJson



def get_default_categories():
    total_count = 4
    categories = []

    categoryTop = Category()
    categoryTop.id = "top"
    categoryTop.name = "Decentraland"
    categoryTop.image = "https://twitter.com/decentraland/photo"
    categoryTop.slug = "/category/top"
    categoryTop.childs = []
    categories.append(categoryTop)

    categoryCollectibles = Category()
    categoryCollectibles.id = "collectibles"
    categoryCollectibles.name = "Collectibles"
    categoryCollectibles.image = "https://peer.decentraland.org/lambdas/collections/contents/urn:decentraland:matic:collections-v2:0xe378518804efb209c8ed97468e7fc59c4db60ef3:0/thumbnail"
    categoryCollectibles.slug = "/category/collectibles"
    categoryCollectibles.childs = []
    categoryTop.childs.append(categoryCollectibles)
    categories.append(categoryCollectibles)

    categoryLand = Category()
    categoryLand.id = "land"
    categoryLand.name = "Land"
    categoryLand.image = "https://market.decentraland.org/contracts/0x959e104e1a4db6317fa58f8295f586e1a978c297/tokens/5476"
    categoryLand.slug = "/category/land"
    categoryLand.childs = []
    categoryTop.childs.append(categoryLand)
    categories.append(categoryLand)

    #---------------------- Collectibles --------------
    
    categoryWearables = Category()
    categoryWearables.id = "wearables"
    categoryWearables.name = "Wearables"
    categoryWearables.image = "https://peer.decentraland.org/lambdas/collections/contents/urn:decentraland:matic:collections-v2:0xe378518804efb209c8ed97468e7fc59c4db60ef3:0/thumbnail"
    categoryWearables.slug = "/category/wearables"
    categoryWearables.childs = []
    categoryCollectibles.childs.append(categoryWearables)
    categories.append(categoryWearables)

    categoryEmotes = Category()
    categoryEmotes.id = "emotes"
    categoryEmotes.name = "Emotes"
    categoryEmotes.image = "https://peer.decentraland.org/lambdas/collections/contents/urn:decentraland:matic:collections-v2:0x9087f96750c4e7607454c67c4f0bcf357ae62a46:1/thumbnail"
    categoryEmotes.slug = "/category/emotes"
    categoryEmotes.childs = []
    categoryCollectibles.childs.append(categoryEmotes)
    categories.append(categoryEmotes)

    categoryNames = Category()
    categoryNames.id = "names"
    categoryNames.name = "Names"
    categoryNames.image = "https://cdn.decentraland.org/@dcl/marketplace-site/5.62.0/static/media/claim-your-own-name.a67d4515.svg"
    categoryNames.slug = "/category/names"
    categoryNames.childs = []
    categoryCollectibles.childs.append(categoryNames)
    categories.append(categoryNames)

    #---------------------- Land --------------

    categoryParcels = Category()
    categoryParcels.id = "parcels"
    categoryParcels.name = "Parcels"
    categoryParcels.image = "https://market.decentraland.org/contracts/0x959e104e1a4db6317fa58f8295f586e1a978c297/tokens/5475"
    categoryParcels.slug = "/category/parcels"
    categoryParcels.childs = []
    categoryLand.childs.append(categoryParcels)
    categories.append(categoryParcels)

    categoryEstates = Category()
    categoryEstates.id = "estates"
    categoryEstates.name = "Estates"
    categoryEstates.image = "https://market.decentraland.org/contracts/0x959e104e1a4db6317fa58f8295f586e1a978c297/tokens/5476"
    categoryEstates.slug = "/category/estates"
    categoryEstates.childs = []
    categoryLand.childs.append(categoryEstates)
    categories.append(categoryEstates)

    return categories


def getCategoryMetadata(category: Category, categorySchemaJson: str):

    products = []

    attributeTypes = []
    if category.name.lower() == "wearables":

        # define decentraland land attribute types
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


    if category.name.lower() == "parcels":

        # define decentraland land attribute types
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

    categoryMetadata = CollectionMetadata(
        name = category.name,   
        description="",
        type = "metaverse", 
        attribute_types = attributeTypes)

    categoryMetadataJson = categoryMetadata.toJSON()

    '''
    print("Decentraland Category Metadata")
    print("------------------------------------")
    print(categoryMetadataJson)
    print("------------------------------------")

    print("Decentraland Category Metadata Schema")
    print("------------------------------------")
    print(categorySchemaJson)
    print("------------------------------------")
    '''
    #validate metadata
    print("validate schema")
    validate_json(categoryMetadataJson, categorySchemaJson)
    print("schema validated ")

    return categoryMetadataJson


def get_parent_category(categories, categoryId):

    for category in categories:
        if category.childs:
            for child in category.childs:
                if child.id == categoryId:
                    return category
   
    return None

def synch_category_list(current_page, page_size, search, sort, **kwargs):

    #print("connect to Web3")
    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    #print("connect to IPFS")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    name = "decentraland category factory"
    symbol = "dec"
    
    print("construct category factory: " + name)
    categoryContractFactory = constructCollectionFactory(w3, name, symbol)
    print("latest ========> created new category contract factory: " + categoryContractFactory.address)
    
    ownerPrivateKey = os.environ.get('ETHEREUM_PRIVATE_KEY')
    ownerPublicAddress = os.environ.get('ETHEREUM_PUBLIC_ADDRESS')

    # create category NFT's
    catalog_categories = get_default_categories()
    for catalog_category in catalog_categories:

        print("create category NFT: " + catalog_category.name)

        categorySchema = getCollectionSchema()
        categoryMetadata = getCategoryMetadata(catalog_category, categorySchema)
        categoryMetadataHash = ipfsclient.add_str(categoryMetadata)

        categoryUri = "ipfs://" + categoryMetadataHash

        nonce1 = w3.eth.get_transaction_count(ownerPublicAddress) 
        transaction = categoryContractFactory.functions.mint(categoryUri).build_transaction({
                'from': ownerPublicAddress,
                'gas' : 8000000,
                'nonce': nonce1,
            })
        signed_tx = w3.eth.account.sign_transaction(transaction, ownerPrivateKey)
        txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

        vals = array.array('B', txn_receipt1.logs[0].topics[3])
        tokenId = vals[len(vals) - 1]

        print("tokenId: " + str(tokenId))

        catalog_category.tokenId = tokenId

        parent = get_parent_category(catalog_categories, catalog_category.id)
        if parent != None:

            print("add child token to parent")

            # add child to parent
            nonce1 = w3.eth.get_transaction_count(ownerPublicAddress) 
            transaction = categoryContractFactory.functions.nestTransferFrom(
                ownerPublicAddress,
                categoryContractFactory.address,
                tokenId,
                parent.tokenId,
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
            transaction = categoryContractFactory.functions.acceptChild(
                parent.tokenId,
                0,
                categoryContractFactory.address,
                tokenId
            ).build_transaction({
                    'from': ownerPublicAddress,
                    'gas' : 8000000,
                    'nonce': nonce1,
                })
            signed_tx = w3.eth.account.sign_transaction(transaction, ownerPrivateKey)
            txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

            print("done adding child")

        

        


    c = []
    total_count = 0

    #print("(Rich) return categories:  " + str(c))
    

    return c, total_count
 

def retrieve_asset_list(collection_slug):

    #print("connect to Web3")
    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    ownerPrivateKey = os.environ.get('ETHEREUM_PRIVATE_KEY')
    ownerPublicAddress = os.environ.get('ETHEREUM_PUBLIC_ADDRESS')

    #print("connect to IPFS")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    assetsContractFactory = constructItemFactory(w3, "opensea items factory", "osi")
    print("xxxxxxxxxxxxxxxxxxxxxxxxx   created asset contract factory: " + assetsContractFactory.address)

    categoryAddress = os.environ.get('CATEGORY_CONTRACT')
    categoryContractFactory = get_collection_contract(w3, categoryAddress)

    # get opensea collections dictionary
    print("Get OpenSea collection data")
    openSeaApiKey = os.environ.get('OPENSEA_APIKEY')
    
    oAPI = OpenseaAPI(apikey=openSeaApiKey)
    result = oAPI.collection(collection_slug=collection_slug)

    #print(type(result))
    #json_object = json.dumps(result, indent = 4) 
    #print("------------------------------------")
    #print(json_object)
    #print("------------------------------------")


    # get collection from dictionary and create collection object
    print("get OpenSea " + collection_slug + " Collections")
    collectionResults = result.get("collection")

    #print("coll: " + str(collectionResults))
    #openSeaCollections = OpenSeaCollection.from_dict(collectionResults)

    print("process OpenSea " + collection_slug + " Collections")

    for openSeaCollection in collectionResults.get("primary_asset_contracts"):

        print("get collection")

        name = openSeaCollection.get("name")
        symbol = openSeaCollection.get("symbol")
        description = openSeaCollection.get("description")
        contractAddress = openSeaCollection.get("address")
        imageUrl = openSeaCollection.get("image_url")
        
        print("opensea collection: " + name + ", symbol: " + symbol + ", description: " + description + ", contractAddress: " + contractAddress)

        #productContractName = productContract.functions.name().call()
        #productContractSymbol = productContract.functions.symbol().call()

        print("get openSea assets")
        assetsResults = oAPI.assets(asset_contract_address=contractAddress)
        openSeaAssets = assetsResults.get("assets")
        for openSeaAssetDict in openSeaAssets:

            print(type(result))
            json_object = json.dumps(openSeaAssetDict, indent = 4) 
            #print("------------------------------------")
            #print(json_object)
            #print("------------------------------------")

            print("convert asset to class")
            openSeaAsset = OpenSeaAsset.from_dict(openSeaAssetDict)

            print("create asset: " + openSeaAsset.name)
            id = openSeaAsset.id
            name = openSeaAsset.name
            description = openSeaAsset.description
            tokenId = openSeaAsset.token_id
            imageUrl = openSeaAsset.image_url

            print("construct asset metadata")
            assetSchema = getItemSchema()
            assetMetadata = getAssetMetadata(tokenId, openSeaAsset, assetSchema)
            assetMetadataHash = ipfsclient.add_str(assetMetadata)

            assetUri = "ipfs://" + assetMetadataHash

            nonce1 = w3.eth.get_transaction_count(ownerPublicAddress) 
            transaction = assetsContractFactory.functions.mint(assetUri).build_transaction({
                    'from': ownerPublicAddress,
                    'gas' : 8000000,
                    'nonce': nonce1,
                })
            signed_tx = w3.eth.account.sign_transaction(transaction, ownerPrivateKey)
            txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

            vals = array.array('B', txn_receipt1.logs[0].topics[3])
            assetNFTTokenId = vals[len(vals) - 1]

            # add asset to category nft
            
            parcelsTokenId = int(os.environ.get('PARCELS_TOKEN_ID'))
            wearablesTokenId = int(os.environ.get('WEARABLES_TOKEN_ID'))

            print("add asset to parcels: " + str(categoryAddress) + "-" + str(parcelsTokenId))
            categoryTokenId = parcelsTokenId


            # add child asset to parent collection
            print("add asset to category")
            nonce1 = w3.eth.get_transaction_count(ownerPublicAddress) 
            transaction = assetsContractFactory.functions.nestTransferFrom(
                ownerPublicAddress,
                categoryAddress,
                assetNFTTokenId,
                categoryTokenId,
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
            transaction = categoryContractFactory.functions.acceptChild(
                categoryTokenId,
                0,
                assetsContractFactory.address,
                assetNFTTokenId
            ).build_transaction({
                    'from': ownerPublicAddress,
                    'gas' : 8000000,
                    'nonce': nonce1,
                })
            signed_tx = w3.eth.account.sign_transaction(transaction, ownerPrivateKey)
            txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

            print("asset has been added to catalog")

        
        break
        
def synch_asset_list(current_page, page_size, search, sort, **kwargs):

    retrieve_asset_list("decentraland")

    #retrieve_asset_list("decentraland-wearables")
    


    #print("(Rich) return products:  " + str(p))
    p = []
    total_count = 0

    return p, total_count

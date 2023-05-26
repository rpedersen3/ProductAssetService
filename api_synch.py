import json
import jsonschema
from jsonschema import validate

import re
import solcx
import array

import graphene
from graphene import ObjectType

from web3 import Web3
from web3.middleware import geth_poa_middleware

import ipfshttpclient

from constants import erc165ABI, erc721ABI, ERC721InterfaceId, BlockSetId, NFTContractSetId
from helper import FilterVisibility, SortEnum

from api_category import Categories, Category

from catalog_metadata_schema import CatalogMetadataSchema
from catalog_metadata import CatalogMetadata

from category_metadata_schema import CategoryMetadataSchema
from category_metadata import CategoryMetadata

from api_product import Products, Product

from product_metadata_schema import ProductMetadataSchema
from product_metadata import ProductMetadata, AttributeTypeMetadata

from asset_metadata_schema import AssetMetadataSchema
from asset_metadata import AssetMetadata, AssetAttributeMetadata

from opensea_decentraland_asset import OpenSeaAsset


from web3.gas_strategies.rpc import rpc_gas_price_strategy


import redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

from opensea import OpenseaAPI

import logging
logger = logging.getLogger(__name__)



class SynchProducts(graphene.Interface):

    products = graphene.List(Product)
    total_count = graphene.Int(required=True)

class SynchProductList(graphene.ObjectType):
    class Meta:
        interfaces = (Products,)


class SynchCategories(graphene.Interface):

    categories = graphene.List(Category)
    total_count = graphene.Int(required=True)

class SynchCategoryList(graphene.ObjectType):
    class Meta:
        interfaces = (Categories,)



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

    synch_products = graphene.Field(
        Products,
        filter=graphene.Argument(SynchFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(SynchSortInput, default_value={})
    )

    synch_categories = graphene.Field(
        Categories,
        filter=graphene.Argument(SynchFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(SynchSortInput, default_value={})
    )
    
    @staticmethod
    def resolve_synch_products(self, info, filter, current_page, page_size, search, sort):
        #print("(Rich) resolve_synch_products => get products: ")
        products, total_count = synch_product_list(
            current_page, page_size, search, sort, **filter)
        
        #print("(Rich) resolve_products => get products return list: ")
        return SynchProductList(products=products, total_count=total_count)
    
    @staticmethod
    def resolve_synch_categories(self, info, filter, current_page, page_size, search, sort):
        #print("(Rich) resolve_synch_categories => get categories: ")
        categories, total_count = synch_category_list(
            current_page, page_size, search, sort, **filter)
        
        return SynchCategoryList(categories=categories, total_count=total_count)

def get_product_abi():
    with open("contracts/productContract.json") as f:
        info_json = json.load(f)
    abi = info_json["abi"]
    return abi

def get_product_bytecode():
    with open("contracts/productContract.bin", "r") as f:
        info_bytecode = f.read()
    return info_bytecode


def get_product_metadata_schema():
    with open("product_schema.json") as f:
        info_json = f.read()
    return info_json



def get_catalog_abi():
    with open("contracts/catalogContract.json") as f:
        info_json = json.load(f)
    abi = info_json["abi"]
    return abi

def get_catalog_bytecode():
    with open("contracts/catalogContract.bin", "r") as f:
        info_bytecode = f.read()
    return info_bytecode

def get_catalog_metadata_schema():
    with open("catalog_schema.json") as f:
        info_json = f.read()
    return info_json




def validate_json(json_data, json_schema):

    try:
        validate(instance=json.loads(json_data), schema=json.loads(json_schema))

    except Exception as e:
        print(str(e))
        return False
    
    #print("validation successful")
    return True



def getCatalogSchema():

    # define product schema
    #productSchema = ProductMetadataSchema()
    #productSchemaJson = productSchema.toJSON()

    catalogSchemaJson = get_catalog_metadata_schema()

    print("Catalog Metadata Schema")
    print("------------------------------------")
    print(catalogSchemaJson)
    print("------------------------------------")

    return catalogSchemaJson

def getCategorySchema():

    # define decentraland nft schema
    categorySchema = CategoryMetadataSchema()
    categorySchemaJson = categorySchema.toJSON()

    print("NFT Category Schema ")
    print("------------------------------------")
    print(categorySchemaJson)
    print("------------------------------------")

    return categorySchemaJson


def getProductSchema():

    # define product schema
    #productSchema = ProductMetadataSchema()
    #productSchemaJson = productSchema.toJSON()

    productSchemaJson = get_product_metadata_schema()

    print("Product (Collection) Metadata Schema")
    print("------------------------------------")
    print(productSchemaJson)
    print("------------------------------------")

    return productSchemaJson


def getProductMetadata(id, name, description, image, productSchemaJson):

    # define decentraland product

    if name.lower() == "dcl halloween 2019":
        attributeTypes = []
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
        
        
        
    if name.lower() == "decentraland":
        attributeTypes = []
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
    

    productMetadata = ProductMetadata(id=id, name=name, description=description, image=image, attributeTypes=attributeTypes)
    productMetadataJson = productMetadata.toJSON()

    print("Product Metadata")
    print("------------------------------------")
    print(productMetadataJson)
    print("------------------------------------")

    #validate metadata
    print("validate schema")
    validate_json(productMetadataJson, productSchemaJson)
    print("schema validated ")

    return productMetadataJson



def getAssetSchema():

    # define decentraland nft schema
    assetSchema = AssetMetadataSchema()
    assetSchemaJson = assetSchema.toJSON()

    print("NFT Asset Schema ")
    print("------------------------------------")
    print(assetSchemaJson)
    print("------------------------------------")

    return assetSchemaJson

def getAssetMetadata(tokenId: int, openSeaAsset: OpenSeaAsset, assetSchemaJson: str):

    attributes = []
    
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

    assetMetadata = AssetMetadata(
        name = openSeaAsset.name,  
        display_name = openSeaAsset.name,  
        image = openSeaAsset.image_url,
        description="", 
        price = 87.5,
        attributes = attributes)

    assetMetadataJson = assetMetadata.toJSON()
    print("Decentraland Asset Metadata")
    print("------------------------------------")
    print(assetMetadataJson)
    print("------------------------------------")

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

        print("(Rich) wearable add product ")
        product = ProductMetadata(
            id="0xE23c70A215bCb0Aa5b34a1edFF71e367fb70c6Aa",
            name="decentraland-wearables"
        )
        products.append(product)

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

        product = ProductMetadata(
            id="0xf7F8C5e703B973b20F5ceFd9e78896a32E4a0bc9",
            name="Decentraland"
        )
        products.append(product)

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

    categoryMetadata = CategoryMetadata(
        name = category.name,  
        display_name = category.name, 
        image = category.image, 
        description="", 
        products=products,
        attribute_types = attributeTypes)

    categoryMetadataJson = categoryMetadata.toJSON()
    print("Decentraland Category Metadata")
    print("------------------------------------")
    print(categoryMetadataJson)
    print("------------------------------------")

    #validate metadata
    #print("validate schema")
    validate_json(categoryMetadataJson, categorySchemaJson)
    #print("schema validated ")

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

    name = "decentraland catalog"
    symbol = "dec"
    
    print("construct catalog: " + name)

    #print("get catalog abi and bytecode")
    catalogABI = get_catalog_abi()
    catalogBytecode = get_catalog_bytecode()

    account_from = {
        "private_key": "6a55033da457aa2e3442875cf1a6843f8e9d3e2a357d3baf4b2b9c239d0e76d7",
        "address": "0x4FB0032AA225a94EdB257ae1d2338DfDc6d23e7F",
    }

    print("start creating catalog contract ")
    catalogContract = w3.eth.contract(abi=catalogABI, bytecode=catalogBytecode)
    catalog_txn = catalogContract.constructor(name, symbol).build_transaction(
        {
            'from': account_from['address'],
            'nonce': w3.eth.get_transaction_count(account_from['address']),
        }
    )

    print("create catalog contract: " + name + ", symbol: " + symbol)
    tx_create = w3.eth.account.sign_transaction(catalog_txn, account_from['private_key'])
    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("catalog contract address: " + tx_receipt.contractAddress)
    catalogContract = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=catalogABI
    )

    print("latest ========> created new catalog contract: " + tx_receipt.contractAddress)
    

    # set collection metadata
    '''
    print("get catalog schema")
    catalogSchema = getCatalogSchema()
    
    catalogMetadata = getCatalogMetadata("decentraland", "decentraland ...", "", catalogSchema)
    collectionMetadataHash = ipfsclient.add_str(catalogMetadata)

    collectionUri = "ipfs://" + collectionMetadataHash
    transaction = catalogContract.functions.setCollectionUri(collectionUri).build_transaction({
            'from': account_from['address'],
            'gas' : 8000000,
            'nonce': w3.eth.get_transaction_count(account_from['address']),
        })
    signed_tx = w3.eth.account.sign_transaction(transaction, account_from['private_key'])
    txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)
    
    print("xxxxxxxxxxxxxxxxxxxxxxxxx   created new catalog contract: " + tx_receipt.contractAddress)
    '''

    catalog_categories = get_default_categories()

    for catalog_category in catalog_categories:

        print("create category NFT: " + catalog_category.name)

        categorySchema = getCategorySchema()
        categoryMetadata = getCategoryMetadata(catalog_category, categorySchema)
        categoryMetadataHash = ipfsclient.add_str(categoryMetadata)

        categoryUri = "ipfs://" + categoryMetadataHash

        nonce1 = w3.eth.get_transaction_count(account_from['address']) 
        transaction = catalogContract.functions.mint(categoryUri).build_transaction({
                'from': account_from['address'],
                'gas' : 8000000,
                'nonce': nonce1,
            })
        signed_tx = w3.eth.account.sign_transaction(transaction, account_from['private_key'])
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
            nonce1 = w3.eth.get_transaction_count(account_from['address']) 
            transaction = catalogContract.functions.nestTransferFrom(
                account_from['address'],
                tx_receipt.contractAddress,
                tokenId,
                parent.tokenId,
                "0x0000000000000000000000000000000000000000000000000000000000000000"
            ).build_transaction({
                    'from': account_from['address'],
                    'gas' : 8000000,
                    'nonce': nonce1,
                })
            signed_tx = w3.eth.account.sign_transaction(transaction, account_from['private_key'])
            txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

            print("accept child token addition")

            # accept child to parent
            nonce1 = w3.eth.get_transaction_count(account_from['address']) 
            transaction = catalogContract.functions.acceptChild(
                parent.tokenId,
                0,
                tx_receipt.contractAddress,
                tokenId
            ).build_transaction({
                    'from': account_from['address'],
                    'gas' : 8000000,
                    'nonce': nonce1,
                })
            signed_tx = w3.eth.account.sign_transaction(transaction, account_from['private_key'])
            txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

            print("done adding child")

        

        


    c = []
    total_count = 0

    #print("(Rich) return categories:  " + str(c))
    

    return c, total_count
 

def retrieve_product_list(collection_slug):

    #print("connect to Web3")
    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    #print("connect to IPFS")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    # get opensea collections dictionary
    oAPI = OpenseaAPI(apikey="4ef36d35d50844bc8e226113e31e1c56")
    result = oAPI.collection(collection_slug=collection_slug)

    oAPI.collection()
    

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

        #print("get product abi and bytecode")
        productABI = get_product_abi()
        productBytecode = get_product_bytecode()

        account_from = {
            "private_key": "6a55033da457aa2e3442875cf1a6843f8e9d3e2a357d3baf4b2b9c239d0e76d7",
            "address": "0x4FB0032AA225a94EdB257ae1d2338DfDc6d23e7F",
        }

        productContract = w3.eth.contract(abi=productABI, bytecode=productBytecode)
        product_txn = productContract.constructor(name, symbol).build_transaction(
            {
                'from': account_from['address'],
                'nonce': w3.eth.get_transaction_count(account_from['address']),
            }
        )

        #print("create product contract: " + name + ", symbol: " + symbol)
        tx_create = w3.eth.account.sign_transaction(product_txn, account_from['private_key'])
        tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        productContract = w3.eth.contract(
            address=tx_receipt.contractAddress,
            abi=productABI
        )

        # set collection metadata
        #print("get product schema")
        productSchema = getProductSchema()

        #print("get product metadata")
        productMetadata = getProductMetadata(
            contractAddress,
            name,
            description,
            imageUrl,
            productSchema)

        collectionMetadataHash = ipfsclient.add_str(productMetadata)

        collectionUri = "ipfs://" + collectionMetadataHash
        transaction = productContract.functions.setCollectionUri(collectionUri).build_transaction({
                'from': account_from['address'],
                'gas' : 8000000,
                'nonce': w3.eth.get_transaction_count(account_from['address']),
            })
        signed_tx = w3.eth.account.sign_transaction(transaction, account_from['private_key'])
        txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)

        print("xxxxxxxxxxxxxxxxxxxxxxxxx   created new contract: " + tx_receipt.contractAddress)



        #productContractName = productContract.functions.name().call()
        #productContractSymbol = productContract.functions.symbol().call()

        print("get openSea assets")
        assetsResults = oAPI.assets(asset_contract_address=contractAddress)
        openSeaAssets = assetsResults.get("assets")
        for openSeaAssetDict in openSeaAssets:


            #print(type(result))
            #json_object = json.dumps(openSeaAssetDict, indent = 4) 
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
            assetSchema = getAssetSchema()
            assetMetadata = getAssetMetadata(tokenId, openSeaAsset, assetSchema)
            assetMetadataHash = ipfsclient.add_str(assetMetadata)

            assetUri = "ipfs://" + assetMetadataHash

            nonce1 = w3.eth.get_transaction_count(account_from['address']) 
            transaction = productContract.functions.mint(assetUri).build_transaction({
                    'from': account_from['address'],
                    'gas' : 8000000,
                    'nonce': nonce1,
                })
            signed_tx = w3.eth.account.sign_transaction(transaction, account_from['private_key'])
            txn_hash1 = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            txn_receipt1 = w3.eth.wait_for_transaction_receipt(txn_hash1)
        
        break
        
def synch_product_list(current_page, page_size, search, sort, **kwargs):

    #retrieve_product_list("decentraland")

    retrieve_product_list("decentraland-wearables")
    


    #print("(Rich) return products:  " + str(p))
    p = []
    total_count = 0

    return p, total_count
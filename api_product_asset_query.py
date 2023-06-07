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

from constants import erc165ABI, erc721ABI, ItemInterfaceId, BlockSetId, NFTContractSetId
from helper import FilterVisibility, SortEnum

from api_attribute import Attribute, AttributeValue

from api_attribute import AttributeType
from api_category import Category, CategoryFilterInput, CategoryList, Categories, CategorySortInput
from constants import CollectionInterfaceId, ItemInterfaceId

from api_product_asset import ProductAsset, ProductAssetFilterInput, ProductAssetList, ProductAssets, ProductAssetSortInput

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



# copied from category, need to make into library
def parse_attribute_types(category, metaAttributeTypes):
    category.attribute_types = []
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

            category.attribute_types.append(attributeType)

def retrieve_category_list(slug):

    categories = []

    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    contractAddress = os.environ.get('CATEGORY_CONTRACT')
    tokenIdStr = slug.replace("/category/", "")

    if "-" in tokenIdStr:
        ids = tokenIdStr.split("-")
        contractAddress = ids[0]
        tokenIdStr = ids[1]

    tokenId = int(tokenIdStr)

    print("get contract: " + contractAddress)
    topCategoryContract = get_collection_contract(w3, contractAddress)
    tokenURI = topCategoryContract.functions.tokenURI(tokenId).call()

    cid = tokenURI.replace("ipfs://", "");
    metadataJson = ipfsclient.cat(cid)

    #print("l0 ipfs data: " + str(metadataJson))
    
    metaCategory = json.loads(metadataJson)
    category = Category()
    category.id = str(topCategoryContract.address) + "-" + str(tokenId)
    category.name = metaCategory.get("name")
    category.image = metaCategory.get("image")
    category.slug = "/category/" + str(topCategoryContract.address) + "-" + str(tokenId)
    category.childs = []

    parse_attribute_types(category, metaCategory.get("attribute_types"))
    categories.append(category)

    childCategoryTokenIds = topCategoryContract.functions.childrenOf(tokenId).call()
    for childCategoryTokenId in childCategoryTokenIds:
        childTokenId = int(childCategoryTokenId[0])
        childAddress = childCategoryTokenId[1]

        childCategoryContract = get_collection_contract(w3, childAddress)
        if childCategoryContract != None:
            
            childTokenURI = childCategoryContract.functions.tokenURI(childTokenId).call()

            cid = childTokenURI.replace("ipfs://", "");
            metadataJson = ipfsclient.cat(cid)
            
            metaCategory = json.loads(metadataJson)

            #print("l1 ipfs data: " + str(metadataJson))

            childCategory = Category()
            childCategory.id = str(childAddress) + "-" + str(childTokenId)
            childCategory.name = metaCategory.get("name")
            childCategory.image = metaCategory.get("image")
            childCategory.slug = "/category/" + str(childAddress) + "-" + str(childTokenId)
            childCategory.childs = []

            parse_attribute_types(childCategory, metaCategory.get("attribute_types"))

            category.childs.append(childCategory)
            categories.append(childCategory)

            level2Categories = childCategoryContract.functions.childrenOf(childTokenId).call()

            for level2Category in level2Categories:
                level2TokenId = int(level2Category[0])
                level2Address = level2Category[1]

                level2CategoryContract = get_collection_contract(w3, level2Address)
                if level2CategoryContract != None:
                    level2TokenURI = level2CategoryContract.functions.tokenURI(level2TokenId).call()
                    cid = level2TokenURI.replace("ipfs://", "");
                    metadataJson = ipfsclient.cat(cid)
                    
                    metaCategory = json.loads(metadataJson)

                    #print("l2 ipfs data: " + str(metadataJson))

                    level2Category = Category()
                    level2Category.id = str(level2Address) + "-" + str(level2TokenId)
                    level2Category.name = metaCategory.get("name")
                    level2Category.image = metaCategory.get("image")
                    level2Category.slug = "/category/" + str(level2Address) + "-" + str(level2TokenId)
                    level2Category.childs = []

                    parse_attribute_types(level2Category, metaCategory.get("attribute_types"))

                    childCategory.childs.append(level2Category)
                    categories.append(level2Category)
    return categories

class ProductAssetQuery(graphene.ObjectType):
    productAsset = graphene.Field(
        ProductAsset,
        id=graphene.String(default_value=None),
        slug=graphene.String(default_value=None),
        barcode=graphene.String(default_value=None),
    )
    productAssets = graphene.Field(
        ProductAssets,
        filter=graphene.Argument(ProductAssetFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(ProductAssetSortInput, default_value={})
    )
    

    @staticmethod
    def resolve_productAsset(self, info, id=None, slug=None, barcode=None):

        if id:
            print("(Rich) resolve product_asset for id: " + str(id))
            #product = Product.search([('id', '=', id)], limit=1)
        elif slug:
            slug = slug.replace("/product-asset/", "")
            print("(Rich) resolve product_asset for slug: " + str(slug))
            ids = slug.split("-")
            productId = ids[len(ids)-2]
            assetId = ids[len(ids)-1]
            #print("(Rich) resolve product_asset for id from slug: " + str(assetId))
            #product = Product.search([('website_slug', '=', slug)], limit=1)
        elif barcode:
            print("(Rich) resolve product_asset for barcode: " + str(barcode))
            #product = Product.search([('barcode', '=', barcode)], limit=1)
        else:
            print("(Rich) resolve product_asset not defined ")
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

        productAsset = ProductAsset()
        productAsset.id = str(tokenId)
        #productAsset.product = product
        productAsset.tokenId = tokenId
        productAsset.name = metaAsset.get("name")
        productAsset.display_name = metaAsset.get("display_name")
        #productAsset.description = assetMetadata["description"]
        productAsset.image = metaAsset.get("image")
        productAsset.slug = "/product-asset/" + nftContractAddress + "-" + str(tokenId)
        productAsset.attribute_values = []

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
            productAsset.attribute_values.append(attributeValue)


        print("(Rich) product asset found: " + str(productAsset))
        return productAsset

    @staticmethod
    def resolve_productAssets(self, info, filter, current_page, page_size, search, sort):
        print("(Rich) resolve_productAssets => get productAssets: ")
        if filter != None:
            print("   filter: " + str(filter))

        productAssets, total_count, attribute_values, min_price, max_price = get_product_asset_list(
            current_page, page_size, search, sort, filter)
        
        #print("(Rich) resolve_productAssets => get productAssets return list: ")
        return ProductAssetList(productAssets=productAssets, total_count=total_count, attribute_values=attribute_values,
                    min_price=min_price, max_price=max_price)
    

   
def get_product_asset_list(current_page, page_size, search, sort, filter: ProductAssetFilterInput):

    categories = []

    # get list of product contracts
    if filter.category_slug != None:
        # get list from category
        print("(Rich) ************* filter product assets by category slug: " + filter.category_slug)

        categories = retrieve_category_list(filter.category_slug)



    #print("(Rich) get assets for these categories: " + str(categories))

    #print("connect to Web3")
    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)


    total_count = 0
    p = []
    attribute_values = []

     
    #print("connect to IPFS")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    
    for category in categories:

        # get children assets of categories
        ids = category.id.split("-")
        categoryContractAddress = ids[0]
        categoryTokenId = int(ids[1])

        categoryContract = get_collection_contract(w3, categoryContractAddress)
        childCategoryTokenIds = categoryContract.functions.childrenOf(categoryTokenId).call()
        for childCategoryTokenId in childCategoryTokenIds:
            assetTokenId = childCategoryTokenId[0]
            assetAddress = childCategoryTokenId[1]

            
            assetContract = get_item_contract(w3, assetAddress)
            if assetContract != None:
                print("process asset contract: " + assetAddress)

                filterAsset = True

                tokenURI = assetContract.functions.tokenURI(assetTokenId).call()

                cid = tokenURI.replace("ipfs://", "");
                metadataJson = ipfsclient.cat(cid)
                
                metaAsset = json.loads(metadataJson)

                #print("ipfs data: " + str(metadataJson))

                productAsset = ProductAsset()
                productAsset.id = assetAddress + "-" + str(assetTokenId)
                #productAsset.product = product
                productAsset.tokenId = assetTokenId
                productAsset.name = metaAsset.get("name")
                productAsset.display_name = metaAsset.get("display_name")
                #productAsset.description = assetMetadata["description"]
                productAsset.image = metaAsset.get("image")
                productAsset.slug = "/product-asset/" + assetAddress + "-" + str(assetTokenId)
                productAsset.attribute_values = []

                metaAttributes = metaAsset.get("attributes")
                for metaAttribute in metaAttributes:

                    #print("meta attribute: " + str(metaAttribute))

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

                    #print("product asset =>  attribute values : " + str(attributeValue))
                    productAsset.attribute_values.append(attributeValue)

                #print('append product asset: ' + str(productAsset))
                total_count += 1

                if filterAsset:
                    p.append(productAsset)


    #print("(Rich) return product assets:  " + str(p))
    return p, total_count, attribute_values, 0.0, 0.0


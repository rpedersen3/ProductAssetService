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
from api_product import Product
from api_category import Category, CategoryFilterInput, CategoryList, Categories, CategorySortInput




import redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

import logging
logger = logging.getLogger(__name__)




def parse_products(category, metaProducts):

    category.products = []
    if metaProducts != None:
        for metaProduct in metaProducts:

            print("++++++++++ add product to category: " + metaProduct.get("name"))

            product = Product()
            product.id = metaProduct.get("id")
            product.name = metaProduct.get("name")

            category.products.append(product)


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


def retrieve_category(slug):

    print("connect to blockchain on http://localhost:8546")

    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    print("connect to ipfs on /ip4/127.0.0.1/tcp/5001")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    nftContractAddress = os.environ.get('CATEGORY_CONTRACT')

    print("retrieve category contract")
    with open("contracts/collectionContract.json") as f:
        info_json = json.load(f)
    catABI = info_json

    categoryContract = w3.eth.contract(address=nftContractAddress, 
                                    abi=catABI)

    tokenId = int(slug.replace("/category/", ""));

    tokenURI = categoryContract.functions.tokenURI(tokenId).call()

    print("retrieve category metadata")
    cid = tokenURI.replace("ipfs://", "");
    metadataJson = ipfsclient.cat(cid)

    #print("l0 ipfs data: " + str(metadataJson))
    
    metaCategory = json.loads(metadataJson)
    category = Category()
    category.id = str(tokenId)
    category.name = metaCategory.get("display_name")
    category.image = metaCategory.get("image")
    category.slug = "/category/" + str(tokenId)
    category.childs = []

    parse_products(category, metaCategory.get("products"))
    parse_attribute_types(category, metaCategory.get("attribute_types"))


    childCategoryTokenIds = categoryContract.functions.childrenOf(tokenId).call()
    for childCategoryTokenId in childCategoryTokenIds:
        childTokenId = childCategoryTokenId[0]
        #contractAddress = childCategory[1]

        childTokenURI = categoryContract.functions.tokenURI(childTokenId).call()

        cid = childTokenURI.replace("ipfs://", "");
        metadataJson = ipfsclient.cat(cid)
        
        metaCategory = json.loads(metadataJson)

        #print("l1 ipfs data: " + str(metadataJson))

        childCategory = Category()
        childCategory.id = str(childTokenId)
        childCategory.name = metaCategory.get("display_name")
        childCategory.image = metaCategory.get("image")
        childCategory.slug = "/category/" + str(childTokenId)
        childCategory.childs = []

        parse_products(childCategory, metaCategory.get("products"))
        parse_attribute_types(childCategory, metaCategory.get("attribute_types"))

        category.childs.append(childCategory)

        level2Categories = categoryContract.functions.childrenOf(childTokenId).call()

        for level2Category in level2Categories:
            level2TokenId = level2Category[0]
            #contractAddress = topCategory[1]

            level2TokenURI = categoryContract.functions.tokenURI(level2TokenId).call()
            cid = level2TokenURI.replace("ipfs://", "");
            metadataJson = ipfsclient.cat(cid)
            
            metaCategory = json.loads(metadataJson)

            #print("l2 ipfs data: " + str(metadataJson))

            level2Category = Category()
            level2Category.id = str(level2TokenId)
            level2Category.name = metaCategory.get("display_name")
            level2Category.image = metaCategory.get("image")
            level2Category.slug = "/category/" + str(level2TokenId)
            level2Category.childs = []

            parse_products(level2Category, metaCategory.get("products"))
            parse_attribute_types(level2Category, metaCategory.get("attribute_types"))

            childCategory.childs.append(level2Category)
    
    return category

class CategoryQuery(graphene.ObjectType):

    category = graphene.Field(
        Category,
        id=graphene.Int(default_value=None),
        slug=graphene.String(default_value=None)
    )
    
    categories = graphene.Field(
        Categories,
        filter=graphene.Argument(CategoryFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(CategorySortInput, default_value={})
    )
    

    
    
    @staticmethod
    def resolve_category(self, info, id=None, slug=None):

        print("**************  get category: " + str(id) + " slug: " + str(slug))
        return retrieve_category(slug)
    
    
    @staticmethod
    def resolve_categories(self, info, filter, current_page, page_size, search, sort):

        topCategorySlug = "/category/1"
        if filter != None and filter.slug != None:
            topCategorySlug = filter.slug

        total_count = 4

        print("get categories for this top slug: " + topCategorySlug)
        topCategory = retrieve_category(topCategorySlug)
        categories = topCategory.childs
        print("return the children: " + str(categories))

        return CategoryList(categories=categories, total_count=total_count)
    
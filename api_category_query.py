from typing import List

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

from api_attribute import AttributeType, Facet
from api_category import Category, CategoryFilterInput, CategoryList, Categories, CategorySortInput

from constants import CollectionInterfaceId, ItemInterfaceId


import redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

import logging
logger = logging.getLogger(__name__)




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

def add_facets(facets, metaAttributeTypes: List[AttributeType], attributeFilter):

    for metaAttributeType in metaAttributeTypes:

        # add facet
        facet = Facet()
        facet.id = metaAttributeType.name
        facet.name = metaAttributeType.name
        facet.display_name = metaAttributeType.display_name
        facet.struct_type = metaAttributeType.struct_type
        facet.scalar_type = metaAttributeType.scalar_type
        facet.min = metaAttributeType.min
        facet.max = metaAttributeType.max

        if facet.struct_type == 'scalar' and facet.scalar_type == "integer":
            facet.display_type = 'range'
            facet.filtered_min = facet.min
            facet.filtered_max = facet.max
            if attributeFilter:
                facet.filtered_min = attributeFilter.min
                facet.filtered_max = attributeFilter.max

        if facet.struct_type == 'scalar' and facet.scalar_type == "boolean":
            facet.display_type = 'checkbox-list'
            facet.list = []
            facet.list.append("true")
            facet.list.append("false")

        if facet.struct_type == 'list':
            facet.display_type = 'checkbox-list'

        metaList = metaAttributeType.list
        if (metaList != None):
            facet.list = []
            for metaListItem in metaList:
                facet.list.append(metaListItem)
        facet.filtered_list = facet.list;

        facet_found = False
        for existingFacet in facets:
            if existingFacet.name == facet.name:
                facet_found = True

        if facet_found == False: 
            facets.append(facet)
        
def retrieve_category(slug):

    #print("connect to blockchain on http://localhost:8546")

    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    #print("connect to ipfs on /ip4/127.0.0.1/tcp/5001")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    contractAddress = os.environ.get('CATEGORY_CONTRACT')
    tokenIdStr = slug.replace("/category/", "")
    if "-" in tokenIdStr:
        ids = tokenIdStr.split("-")
        contractAddress = ids[0]
        tokenIdStr = ids[1]

    tokenId = int(tokenIdStr)

    #print("retrieve category contract")
    topCategoryContract = get_collection_contract(w3, contractAddress)

    tokenURI = topCategoryContract.functions.tokenURI(tokenId).call()

    #print("retrieve category metadata")
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
    category.facets = []

    parse_attribute_types(category, metaCategory.get("attribute_types"))

    add_facets(category.facets, category.attribute_types, None)

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
            add_facets(category.facets, childCategory.attribute_types, None)

            category.childs.append(childCategory)


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
                    add_facets(category.facets, level2Category.attribute_types, None)

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
        category = retrieve_category(slug)

        return category
    
    
    @staticmethod
    def resolve_categories(self, info, filter, current_page, page_size, search, sort):

        topCategorySlug = "/category/1"
        if filter != None and filter.slug != None:
            topCategorySlug = filter.slug

        total_count = 4

        topCategory= retrieve_category(topCategorySlug)
        categories = topCategory.childs

        return CategoryList(categories=categories, facets=topCategory.facets, total_count=total_count)
    
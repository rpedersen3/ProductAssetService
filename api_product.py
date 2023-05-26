import graphene
from graphene import ObjectType
from graphene.types import generic

from web3 import Web3
from web3.middleware import geth_poa_middleware

import ipfshttpclient

import json
import jsonschema
from jsonschema import validate


from constants import erc165ABI, erc721ABI, ERC721InterfaceId, BlockSetId, NFTContractSetId
from helper import FilterVisibility, SortEnum

from api_attribute_obj import AttributeType, AttributeValue, Attribute, Facet

from api_product_obj import Product, Products, ProductList, ProductFilterInput, ProductSortInput
from api_category_obj import Category




import redis
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

import logging
logger = logging.getLogger(__name__)

def get_abi():
    with open("contracts/productContract.json") as f:
        info_json = json.load(f)
    abi = info_json["abi"]
    return abi

def get_bytecode():
    with open("contracts/productContract.bin", "r") as f:
        info_bytecode = f.read()
    return info_bytecode



class ProductQuery(graphene.ObjectType):
    product = graphene.Field(
        Product,
        id=graphene.String(default_value=None),
        slug=graphene.String(default_value=None),
        barcode=graphene.String(default_value=None),
    )
    products = graphene.Field(
        Products,
        filter=graphene.Argument(ProductFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(ProductSortInput, default_value={})
    )

    @staticmethod
    def resolve_product(self, info, id, slug, barcode):
        print("(Rich) resolve product ")

        product = Product()
        product.id = "abc"
        product.name = "test product"
        product.productAddress = "abcdefg"
        product.numberOfAssets = 3
        
        return product
    
    @staticmethod
    def resolve_products(self, info, filter, current_page, page_size, search, sort):

        try:
            print("(Rich) resolve_products => get products: " + str(filter))
            #if filter.range_filters:
            #    print("(Rich) resolve_products => get products: " + filter.range_filters)
            products, total_count, attribute_values, asset_attribute_values, facets, min_price, max_price = get_product_list(
                current_page, page_size, search, sort, filter)
            
            return ProductList(products=products, total_count=total_count,
                            asset_attribute_values=asset_attribute_values, 
                            attribute_values=attribute_values,
                            facets=facets,
                            min_price=min_price, max_price=max_price)
        
        except Exception as e:
            print("(Rich) problem getting products: " + str(e))

def add_products(products, metaProducts):

    if metaProducts != None:
        for metaProduct in metaProducts:
            product = Product()
            product.id = metaProduct.get("id")
            product.name = metaProduct.get("name")
            products.append(product)

    return products


def retrieve_category_products(slug):

    products = []

    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    nftContractAddress = "0x81861607Ea72B3BD21589f4Fce59658D4f0A2b06"

    with open("contracts/catalogContract.json") as f:
        info_json = json.load(f)
    catABI = info_json["abi"]

    categoryContract = w3.eth.contract(address=nftContractAddress, 
                                    abi=catABI)

    tokenId = int(slug.replace("/category/", ""));

    tokenURI = categoryContract.functions.tokenURI(tokenId).call()

    cid = tokenURI.replace("ipfs://", "");
    metadataJson = ipfsclient.cat(cid)

    print("l0 meta: " + str(metadataJson))

    metaCategory = json.loads(metadataJson)
    add_products(products, metaCategory.get("products"))
    #parse_attribute_types(metaCategory.get("attribute_types"))

    childCategoryTokenIds = categoryContract.functions.childrenOf(tokenId).call()
    for childCategoryTokenId in childCategoryTokenIds:
        childTokenId = childCategoryTokenId[0]
        #contractAddress = childCategory[1]

        childTokenURI = categoryContract.functions.tokenURI(childTokenId).call()

        cid = childTokenURI.replace("ipfs://", "");
        metadataJson = ipfsclient.cat(cid)
        
        print("l1 meta: " + str(metadataJson))

        metaCategory = json.loads(metadataJson)
        add_products(products, metaCategory.get("products"))


        level2Categories = categoryContract.functions.childrenOf(childTokenId).call()

        for level2Category in level2Categories:
            level2TokenId = level2Category[0]
            #contractAddress = topCategory[1]

            level2TokenURI = categoryContract.functions.tokenURI(level2TokenId).call()
            cid = level2TokenURI.replace("ipfs://", "");
            metadataJson = ipfsclient.cat(cid)

            print("l2 meta: " + str(metadataJson))
            
            metaCategory = json.loads(metadataJson)
            add_products(products, metaCategory.get("products"))
            #parse_attribute_types(metaCategory.get("attribute_types"))

    
    return products


def get_product_list(current_page, page_size, search, sort, filter: ProductFilterInput):

    productAddresses = []

    # get list of product contracts
    if filter.category_slug != None:
        # get list from category
        print("(Rich) ************* filter products by category slug: " + filter.category_slug)
        products = retrieve_category_products(filter.category_slug)
        if len(products) > 0:
            for product in products:
                productAddresses.append(product.id)

    elif filter.contract_address != None:
        productAddresses.append(filter.contract_address)

    else:
        # get list from redis cach that came from blocks
        nftContractSet = r.smembers(NFTContractSetId)
        for nftContractAddress in nftContractSet:
            productAddresses.append(nftContractAddress) 
            
    print("connect to Web3")
    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    print("connect to IPFS")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    numberOfBlocks = w3.eth.block_number
    index = numberOfBlocks
        
    p = []
    attribute_values = []
    facets = []

    nameFilter = None
    if "name" in filter:
        nameFilter = filter.name

    #contractAddressFilter = None
    #if "contract_address" in filter:
    #    contractAddressFilter = filter.contract_address

    #contractAddressFilter = None #"0xf7F8C5e703B973b20F5ceFd9e78896a32E4a0bc9"

    minNumberOfAssetsFilter = None
    if "min_number_of_assets" in filter:
        minNumberOfAssetsFilter = filter.min_number_of_assets

    #if "range_filters" in filter:
    #    for range_filter in filter.range_filters:
    #        print("range filters: " + str(range_filter.name) + "," + str(range_filter.min) + ", " + str(range_filter.max))

    asset_attribute_values = []

    total_count = 0
    for nftContractAddress in productAddresses:
        #if contractAddressFilter == None or contractAddressFilter == nftContractAddress:
            try:  
                productABI = get_abi() 
                erc721Contract = w3.eth.contract(address=nftContractAddress, 
                                            abi=productABI)
        
                contractName = erc721Contract.functions.name().call()
                collectionUri = erc721Contract.functions.getCollectionUri().call()
                totalSupply = erc721Contract.functions.totalSupply().call()
                totalSupply = 20

                print("product name: " + contractName + ", total supply: " + str(totalSupply))

                cid = collectionUri.replace("ipfs://", "");
                metadataJson = ipfsclient.cat(cid)
                metaProduct = json.loads(metadataJson)

                

                found = True
                if nameFilter != None:
                    if nameFilter != contractName:
                        found = False



                if minNumberOfAssetsFilter != None:
                    if minNumberOfAssetsFilter > totalSupply:
                        found = False

                if found:        
                    product = Product()
                    product.id = nftContractAddress
                    product.name = contractName
                    product.productAddress = nftContractAddress
                    product.numberOfAssets = totalSupply

                    product.attributes = []
                    product.attributeValues = []
                    metaAttributeTypes = metaProduct.get("attributeTypes")
                    for metaAttributeType in metaAttributeTypes:

                        attributeFilter = None
                        if "range_filters" in filter:
                            for range_filter in filter.range_filters: 
                                if range_filter.name == metaAttributeType.get("name"):
                                    attributeFilter = range_filter

                        # add attribute
                        attribute = Attribute()
                        attribute.id = metaAttributeType.get("name")
                        attribute.name = metaAttributeType.get("name")
                        attribute.display_name = metaAttributeType.get("display_name")
                        attribute.struct_type = metaAttributeType.get("struct_type")
                        attribute.scalar_type = metaAttributeType.get("scalar_type")
                        attribute.min = metaAttributeType.get("min")
                        attribute.max = metaAttributeType.get("max")

                        if attribute.struct_type == 'scalar' and attribute.scalar_type == "integer":
                            attribute.display_type = 'number'

                        if attribute.struct_type == 'scalar' and attribute.scalar_type == "boolean":
                            attribute.display_type = 'checkbox-list'
                            attribute.values = []
                            attribute.values.append("true")
                            attribute.values.append("false")

                        if attribute.struct_type == 'list':
                            attribute.display_type = 'checkbox-list'
                            

                        metaList = metaAttributeType.get("list")
                        if (metaList != None):
                            attribute.values = []
                            for metaListItem in metaList:
                                attribute.values.append(metaListItem)

                        product.attributes.append(attribute)



                        # add facet
                        facet = Facet()
                        facet.id = metaAttributeType.get("name")
                        facet.name = metaAttributeType.get("name")
                        facet.display_name = metaAttributeType.get("display_name")
                        facet.struct_type = metaAttributeType.get("struct_type")
                        facet.scalar_type = metaAttributeType.get("scalar_type")
                        facet.min = metaAttributeType.get("min")
                        facet.max = metaAttributeType.get("max")
                        

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

                        metaList = metaAttributeType.get("list")
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

                    

                    p.append(product)
                    total_count += 1


                    #print("************* total assets: " + str(totalSupply))
                    for tokenId in range(0, totalSupply):

                        tokenURI = erc721Contract.functions.tokenURI(tokenId).call()
                        #print("token(" + str(tokenId) + ") uri: " + str(tokenURI))

                        cid = tokenURI.replace("ipfs://", "");
                        metadataJson = ipfsclient.cat(cid)

                        
                        metaAsset = json.loads(metadataJson)
                        metaAttributes = metaAsset.get("attributes")

                        for metaAttribute in metaAttributes:

                            #print("************* metaAttribute: " + str(metaAttribute))

                            id = metaAttribute.get("id")

                            attributeValue = AttributeValue()
                            attributeValue.id = id
                            attributeValue.type = metaAttribute.get("type")
                            attributeValue.display_type = metaAttribute.get("display_type")
                            attributeValue.value = metaAttribute.get("value")

                            # set attribute
                            for attribute in product.attributes:
                                if attribute.name.lower() == metaAttribute.get("type").lower():
                                    attributeValue.attribute = attribute
                                    break

                            #displayType = "checkbox"
                            #if (metaAttribute.get("display_type") == "number"):
                            #    displayType = "number"
                            #attributeValue.display_type =  displayType;

                            asset_attribute_values.append(attributeValue)
                            
            except Exception as e:
                message = 'contract construction exception: ' + str(e)
                print('********************* contract construction exception: ' + str(e))


    



    

    #print("(Rich) return asset attribute values:  " + str(asset_attribute_values))
    return p, total_count, attribute_values, asset_attribute_values, facets, 0.0, 0.0
import graphene
from graphene import ObjectType
from graphene.types import generic

import ipfshttpclient

import json
import jsonschema
from jsonschema import validate



from web3 import Web3
from web3.middleware import geth_poa_middleware

from constants import erc165ABI, erc721ABI, ERC721InterfaceId, BlockSetId, NFTContractSetId
from helper import FilterVisibility, SortEnum

from api_attribute_obj import Attribute, AttributeValue
from api_product_obj import Product

from api_product_asset_obj import ProductAsset, ProductAssetFilterInput, ProductAssetList, ProductAssets, ProductAssetSortInput

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
        
        metaCategory = json.loads(metadataJson)
        add_products(products, metaCategory.get("products"))


        level2Categories = categoryContract.functions.childrenOf(childTokenId).call()

        for level2Category in level2Categories:
            level2TokenId = level2Category[0]
            #contractAddress = topCategory[1]

            level2TokenURI = categoryContract.functions.tokenURI(level2TokenId).call()
            cid = level2TokenURI.replace("ipfs://", "");
            metadataJson = ipfsclient.cat(cid)
            
            metaCategory = json.loads(metadataJson)
            add_products(products, metaCategory.get("products"))
            #parse_attribute_types(metaCategory.get("attribute_types"))

    
    return products

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
            print("(Rich) resolve product_asset for slug: " + str(slug))
            ids = slug.split("/")
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
        productAsset.slug = "/product/" + nftContractAddress + "/" + str(tokenId)
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
    

def getERC721Contracts(w3, start, end):

    #r.flushall()
    #print("blocks: " + str(r.smembers(BlockSetId)))
    #print("nft contracts: " + str(r.smembers(NFTContractSetId)))

    for blockNumber in range(start, end):
        if r.sismember(BlockSetId, blockNumber) == False:
            #print("process block: " + str(blockNumber))
            block = w3.eth.get_block(blockNumber, True)
            for transaction in block.transactions:
                #hashStr = transaction['hash'].hex()
                transactionHash = transaction['hash']

                #trans = w3.eth.get_transaction(transId)

                transactionContractAddress = transaction['to']
                #print("to contract address: " + str(transactionContractAddress))

                if transactionContractAddress != None:
                    erc165Contract = w3.eth.contract(address=str(transactionContractAddress), 
                                                    abi=erc165ABI)


                    try:
                        supportsInterface = erc165Contract.functions.supportsInterface(ERC721InterfaceId).call()
                        if supportsInterface == True:

                            if r.sismember(NFTContractSetId, transactionContractAddress) == False:
                                print("add to NFT list: " + str(transactionContractAddress))
                                r.sadd(NFTContractSetId, transactionContractAddress)

                            #print("construct erc721 contract: " + str(transactionContractAddress) ) 
                            erc721Contract = w3.eth.contract(address=transactionContractAddress, 
                                                             abi=erc721ABI) 
                            
                            print("contract name: " + erc721Contract.functions.name().call())

                    except:
                        print("supports interface exception " )  

            r.sadd(BlockSetId, blockNumber)
    
def get_product_asset_list(current_page, page_size, search, sort, filter: ProductAssetFilterInput):

    productAddresses = []

    # get list of product contracts
    if filter.category_slug != None:
        # get list from category
        print("(Rich) ************* filter product assets by category slug: " + filter.category_slug)
        products = retrieve_category_products(filter.category_slug)
        if len(products) > 0:
            for product in products:
                print("(Rich) add product from category filter: " + str(product.id))
                productAddresses.append(product.id)

    elif filter.contract_address != None:
        print("(Rich) add product from address filter: " + str(productAddresses))
        productAddresses.append(productAddresses)

    else:
        # get list from redis cach that came from blocks
        nftContractSet = r.smembers(NFTContractSetId)
        for nftContractAddress in nftContractSet:
            print("(Rich) add product from list in cache: " + str(nftContractAddress))
            productAddresses.append(nftContractAddress) 

    print("(Rich) get assets for these products: " + str(productAddresses))

    #print("connect to Web3")
    w3 = Web3(Web3.HTTPProvider('http://localhost:8546'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    numberOfBlocks = w3.eth.block_number
    index = numberOfBlocks

    #getERC721Contracts(w3, 0, numberOfBlocks)


    total_count = 0
    p = []
    attribute_values = []

    nameFilter = None
    if filter != None and filter.name != None:
        nameFilter = filter.name

    #contractAddressFilter = None
    #if filter != None and filter.contract_address != None:
    #    contractAddressFilter = filter.contract_address


    #contractAddressFilter = "0xf7F8C5e703B973b20F5ceFd9e78896a32E4a0bc9"
            
    #print("connect to IPFS")
    ipfsclient = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

    
    for nftContractAddress in productAddresses:
        try:
            erc721Contract = w3.eth.contract(address=nftContractAddress, 
                                        abi=erc721ABI)

            totalSupply = erc721Contract.functions.totalSupply().call()
            contractName = erc721Contract.functions.name().call()
            contractSymbol = erc721Contract.functions.symbol().call()

            #print("contract: " + contractName + ", address: " + nftContractAddress)

            found = True
            if nameFilter != None:
                if nameFilter != contractName:
                    #print("filter on name")
                    found = False

            #if contractAddressFilter != None:
            #    if contractAddressFilter != nftContractAddress:
            #        #print("filter on contract address: " + str())
            #        found = False

            if found:   
                print("(Rich) get product assets: " + contractName + "; supply: " + str(totalSupply))
                totalSupply = 20

                product = Product()
                product.id = contractName
                product.name = contractName
                product.productAddress = nftContractAddress
                product.numberOfAssets = totalSupply

                for tokenId in range(1, totalSupply):
                    filterAsset = True

                    tokenURI = erc721Contract.functions.tokenURI(tokenId).call()
                    print("token(" + str(tokenId) + ") uri: " + str(tokenURI))

                    cid = tokenURI.replace("ipfs://", "");
                    metadataJson = ipfsclient.cat(cid)
                    
                    metaAsset = json.loads(metadataJson)

                    print("ipfs data: " + str(metadataJson))

                    productAsset = ProductAsset()
                    productAsset.id = str(tokenId)
                    productAsset.product = product
                    productAsset.tokenId = tokenId
                    productAsset.name = metaAsset.get("name")
                    productAsset.display_name = metaAsset.get("display_name")
                    #productAsset.description = assetMetadata["description"]
                    productAsset.image = metaAsset.get("image")
                    productAsset.slug = "/product/" + nftContractAddress + "/" + str(tokenId)
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
                                print("(Rich) ************  not pass filter: " + attributeFilter.name)

                        #print("product asset =>  attribute values : " + str(attributeValue))
                        productAsset.attribute_values.append(attributeValue)

                    #print('append product asset: ' + str(productAsset))
                    total_count += 1

                    if filterAsset:
                        p.append(productAsset)

                    '''
                    productAsset.slug = "/product/" + str(asset.default_code) + "-" + str(asset.id)
                    productAsset.small_image = '/web/image/product.asset/{}/image_128'.format(asset.id)
                    productAsset.image = '/web/image/product.asset/{}/image_1920'.format(asset.id)
                    productAsset.image_filename = str(asset.default_code)

                    

                    productAsset.attribute_values = []
                    
                    for combination in asset.combination_ids:

                        #print("(Rich) add asset combination to attribute value list:  " + str(combination.product_attribute_id.name))

                        productAttribute = ProductAssetAttribute(combination.product_attribute_id.id)
                        productAttribute.name = combination.product_attribute_id.name

                        
                        productAttributeValue = ProductAssetAttributeValue(combination.id)
                        productAttributeValue.name = combination.attribute_value
                        productAttributeValue.value = combination.attribute_value
                        productAttributeValue.attribute = productAttribute

                        attribute_values.append(productAttributeValue)
                        productAsset.attribute_values.append(productAttributeValue)
                    '''

                    
                    
        except Exception as e:
            message = 'contract construction exception: ' + str(e)
            print('contract construction exception: ' + str(e))


    '''

    #while index > numberOfBlocks - 300:
    #    index -= 1

    #    #print ("block(" + str(index) + ") ")
    #    block = w3.eth.get_block(index)
    #    #print ("block(" + str(index) + ") done ")
    #    ##print ("block(" + str(index) + ") " + str(block))
    #    #print ("block ts(" + str(index) + ") " + str(block.items["transactions"]))   



    # First offset is 0 but first page is 1
    if current_page > 1:
        offset = (current_page - 1) * page_size
    else:
        offset = 0

    #order = get_search_order(sort)
    order = 'id ASC'

    #print("(Rich) search products ")
    products = []

    #print("(Rich) product_asset => search products:  " + str(products))

    

    # If attribute values are selected, we need to get the full list of attribute values and prices
    #if domain == partial_domain:
    #    attribute_values = products.mapped('asset_attribute_value_ids')
    #    prices = products.mapped('list_price')
    #    #print("(Rich) partial_domain get attributes and pricing:  " + str(attribute_values))
    #else:
    #    without_attributes_products = Product.search(partial_domain)
    #    attribute_values = without_attributes_products.mapped('asset_attribute_value_ids')
    #    prices = without_attributes_products.mapped('list_price')
    #    #print("(Rich) not partial_domain get attributes and pricing:  " + str(attribute_values))
    
    total_count = len(products)
    products = products[offset:offset + page_size]
    #if prices:
    #    return products, total_count, attribute_values, min(prices), max(prices)
    
    #print("(Rich) search product assets results:  " + str(products))

    

    total_count = 0
    for product in products:
        #print("(Rich) create product asset:  " + str(product))
        #print("(Rich) create product asset ids:  " + str(product.product_asset_ids))
        
        attribute_values = []
        for asset in product.product_asset_ids:

            all_found = True
            if kwargs.get('attribute_value_id', False):
                #print("(Rich) check filter:  " + str(kwargs['attribute_value_id']))
                for filter_attribute_value_id in kwargs['attribute_value_id']:
                    found = False
                    for product_template_attribute_value in asset.product_template_asset_value_ids:

                        #print("(Rich) filter value a:  " + str(product_template_attribute_value))
                        #print("(Rich) filter value b:  " + str(product_template_attribute_value.product_attribute_value_id))

                        if filter_attribute_value_id == product_template_attribute_value.product_attribute_value_id.id:
                            found = True

                    if found == False:
                        all_found = False

            #print("(Rich) found:  " + str(all_found))
            if all_found == True and asset.active == True:

                #    domains.append([('attribute_line_ids.value_ids', 'in', kwargs['attribute_value_id'])])
                #    #print("(Rich) filter by attribute_value_id: " + str(kwargs['attribute_value_id']))
                    
                #print("(Rich) search product assets:  " + str(asset))
                productAsset = ProductAsset(asset.id)
                productAsset.name = asset.name
                productAsset.description = asset.description
                productAsset.slug = "/product/" + str(asset.default_code) + "-" + str(asset.id)
                productAsset.small_image = '/web/image/product.asset/{}/image_128'.format(asset.id)
                productAsset.image = '/web/image/product.asset/{}/image_1920'.format(asset.id)
                productAsset.image_filename = str(asset.default_code)


                productAsset.attribute_values = []
                
                for combination in asset.combination_ids:

                    #print("(Rich) add asset combination to attribute value list:  " + str(combination.product_attribute_id.name))

                    productAttribute = ProductAssetAttribute(combination.product_attribute_id.id)
                    productAttribute.name = combination.product_attribute_id.name

                    
                    productAttributeValue = ProductAssetAttributeValue(combination.id)
                    productAttributeValue.name = combination.attribute_value
                    productAttributeValue.value = combination.attribute_value
                    productAttributeValue.attribute = productAttribute

                    attribute_values.append(productAttributeValue)
                    productAsset.attribute_values.append(productAttributeValue)

                p.append(productAsset)
    '''            

    #print("(Rich) return product assets:  " + str(p))
    return p, total_count, attribute_values, 0.0, 0.0


# Importing Graphene so we can define a simple GraphQL schema
import graphene

from api_category import CategoryQuery, CategoryList
from api_product import ProductQuery, ProductList
from api_product_asset import ProductAssetQuery, ProductAssetList

from api_synch import SynchQuery, SynchProductList, SynchCategoryList

class Query(SynchQuery, CategoryQuery, ProductQuery, ProductAssetQuery):
    pass


schema = graphene.Schema(
    query=Query,
    types=[SynchProductList, SynchCategoryList, CategoryList, ProductList, ProductAssetList]
)

# Importing Graphene so we can define a simple GraphQL schema
import graphene

from api_category_query import CategoryQuery, CategoryList
from api_product_query import ProductQuery, ProductList
from api_product_asset_query import ProductAssetQuery, ProductAssetList


from api_synch import SynchQuery, SynchProductList, SynchCategoryList
from api_synch_feature import SynchFeatureQuery, SynchFeatureList

class Query(SynchQuery, SynchFeatureQuery, CategoryQuery, ProductQuery, ProductAssetQuery):
    pass


schema = graphene.Schema(
    query=Query,
    types=[SynchProductList, SynchCategoryList, SynchFeatureList, CategoryList, ProductList, ProductAssetList]
)

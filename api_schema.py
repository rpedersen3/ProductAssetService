# Importing Graphene so we can define a simple GraphQL schema
import graphene

from api_category_query import CategoryQuery, CategoryList
from api_product_asset_query import ProductAssetQuery, ProductAssetList


from api_synch import SynchQuery, SynchAssetList, SynchCategoryList
from api_synch_feature import SynchFeatureQuery, SynchFeatureList

from api_item_query import ItemQuery, ItemList
from api_collection_query import CollectionQuery, CollectionList

class Query(SynchQuery, SynchFeatureQuery, CategoryQuery, ProductAssetQuery, ItemQuery, CollectionQuery):
    pass


schema = graphene.Schema(
    query=Query,
    types=[SynchAssetList, SynchCategoryList, SynchFeatureList, CategoryList, ProductAssetList, ItemList, CollectionList]
)

import graphene
from graphene import ObjectType
from graphene.types import generic

from helper import FilterVisibility, SortEnum

from api_attribute import AttributeType, Attribute, AttributeValue, Facet


class Product(ObjectType):
    id = graphene.String()
    smallImage = graphene.String()
    price = graphene.Float()
    description = graphene.String()
    image = graphene.String()
    imageFilename = graphene.String()
    slug = graphene.String()
    sku = graphene.String()

    name = graphene.String(required=True)
    productAddress = graphene.String(required=True)

    numberOfAssets = graphene.Int()

    attributes = graphene.List(Attribute)
    attributeValues = graphene.List(AttributeValue)

    is_in_wishlist = graphene.Boolean()
    json_ld = generic.GenericScalar()

class Products(graphene.Interface):

    products = graphene.List(Product)
    total_count = graphene.Int(required=True)
    facets = graphene.List(Facet)
    attribute_values = graphene.List(AttributeValue)
    asset_attribute_values = graphene.List(AttributeValue)
    min_price = graphene.Float()
    max_price = graphene.Float()

class ProductList(graphene.ObjectType):
    class Meta:
        interfaces = (Products,)

class RangeFilterInput(graphene.InputObjectType):
    name = graphene.String()
    min = generic.GenericScalar()
    max = generic.GenericScalar()

class ProductFilterInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int)
    range_filters = graphene.List(RangeFilterInput)
    category_id = graphene.List(graphene.Int)
    category_slug = graphene.String()
    # Deprecated
    attribute_value_id = graphene.List(graphene.Int)
    attrib_values = graphene.List(graphene.String)
    name = graphene.String()
    contract_address = graphene.String()
    min_price = graphene.Float()
    max_price = graphene.Float()
    min_number_of_assets = graphene.Int()


class ProductSortInput(graphene.InputObjectType):
    id = SortEnum()
    name = SortEnum()
    price = SortEnum()

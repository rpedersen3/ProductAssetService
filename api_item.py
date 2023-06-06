import graphene
from graphene import ObjectType
from graphene.types import generic

from helper import FilterVisibility, SortEnum

from api_collection import Collection
from api_attribute import AttributeType, AttributeValue

from attribute_type_metadata import AttributeTypeMetadata

class Item(ObjectType):

    id = graphene.String(required=True)
    
    collection = graphene.Field((lambda: Collection), description='Collection')

    type_id = graphene.String()
    visibility = graphene.Int()
    status = graphene.Int()
    name = graphene.String()
    description = graphene.String()
    display_name = graphene.String()
    sku = graphene.String()
    barcode = graphene.String()
    weight = graphene.Float()
    meta_title = graphene.String()
    meta_keyword = graphene.String()
    meta_description = graphene.String()
    image = graphene.String()
    small_image = graphene.String()
    image_filename = graphene.String()
    thumbnail = graphene.String()
    allow_out_of_stock = graphene.Boolean()
    show_available_qty = graphene.Boolean()
    out_of_stock_message = graphene.String()
    is_in_stock = graphene.Boolean()
    is_in_wishlist = graphene.Boolean()
    qty = graphene.Float()
    slug = graphene.String()
    asset_price = graphene.Float(description='Specific to Product Asset')
    asset_price_after_discount = graphene.Float(description='Specific to Product Asset')
    asset_has_discounted_price = graphene.Boolean(description='Specific to Product Asset')
    is_asset_possible = graphene.Boolean(description='Specific to Product Asset')
    price = graphene.Float(description='Specific to Product Template')
    attribute_values = graphene.List(graphene.NonNull(lambda: AttributeValue),
                                     description='Specific to Product Asset')
    
    json_ld = generic.GenericScalar()

class Items(graphene.Interface):

    items = graphene.List(Item)
    total_count = graphene.Int(required=True)
    attribute_values = graphene.List(AttributeValue)
    min_price = graphene.Float()
    max_price = graphene.Float()

class ItemList(graphene.ObjectType):
    class Meta:
        interfaces = (Items,)

class RangeFilterInput(graphene.InputObjectType):
    name = graphene.String()
    min = graphene.String()
    max = graphene.String()

class ItemFilterInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int)
    category_id = graphene.List(graphene.Int)
    category_slug = graphene.String()
    # Deprecated
    attribute_value_id = graphene.List(graphene.Int)
    attrib_values = graphene.List(graphene.String)
    name = graphene.String()
    contract_address = graphene.String()
    min_price = graphene.Float()
    max_price = graphene.Float()
    range_filters = graphene.List(RangeFilterInput)


class ItemSortInput(graphene.InputObjectType):
    id = SortEnum()
    name = SortEnum()
    price = SortEnum()

import graphene
from graphene import ObjectType
from graphene.types import generic

from helper import FilterVisibility, SortEnum

from api_attribute import AttributeType

class Collection(ObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    image = graphene.String()
    parent = graphene.Field(lambda: Collection)
    childs = graphene.List(graphene.NonNull(lambda: Collection))
    slug = graphene.String()

    attribute_types = graphene.List(graphene.NonNull(lambda: AttributeType))
    json_ld = generic.GenericScalar()

    tokenId = graphene.Int()

    def resolve_parent(self, info):
        return self.parent or None

    def resolve_childs(self, info):
        return self.childs or None
    
    def resolve_products(self, info):
        return self.products or None
    
    def resolve_attribute_types(self, info):
        return self.attribute_types or None

    def resolve_slug(self, info):
        return self.slug

    def resolve_json_ld(self, info):
        return self.get_json_ld()

class Collections(graphene.Interface):
    collections = graphene.List(Collection)
    total_count = graphene.Int(required=True)

class CollectionList(graphene.ObjectType):
    class Meta:
        interfaces = (Collections,)

class CollectionFilterInput(graphene.InputObjectType):
    id = graphene.List(graphene.String)
    slug = graphene.String()
    parent = graphene.Boolean()
    collection_address = graphene.String()
    collection_token_id = graphene.Int()


class CollectionSortInput(graphene.InputObjectType):
    id = SortEnum()
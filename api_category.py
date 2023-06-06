import graphene
from graphene import ObjectType
from graphene.types import generic

from helper import FilterVisibility, SortEnum

from api_attribute import AttributeType
from api_product import Product

class Category(ObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    image = graphene.String()
    parent = graphene.Field(lambda: Category)
    childs = graphene.List(graphene.NonNull(lambda: Category))
    slug = graphene.String()
    products = graphene.List(graphene.NonNull(lambda: Product))
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

class Categories(graphene.Interface):
    categories = graphene.List(Category)
    total_count = graphene.Int(required=True)

class CategoryList(graphene.ObjectType):
    class Meta:
        interfaces = (Categories,)

class CategoryFilterInput(graphene.InputObjectType):
    id = graphene.List(graphene.String)
    slug = graphene.String()
    parent = graphene.Boolean()


class CategorySortInput(graphene.InputObjectType):
    id = SortEnum()
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



class AttributeType(ObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    display_name = graphene.String()


    # scalar, range, list, ...
    struct_type = graphene.String()

    # string, integer, bool, ..
    scalar_type = graphene.String()

    # textbox, radio, dropdown, multi-radio, selection, multi-selection, checkbox, multi-checkbox
    # range, price, color, checkbox
    display_type = graphene.String()

    filter_visibility = FilterVisibility()

    # struct_type: scalar or range
    min = generic.GenericScalar()
    filtered_min = generic.GenericScalar()

    max = generic.GenericScalar()
    filtered_max = generic.GenericScalar()

    # struct_type: select or multi-select
    list = graphene.List(generic.GenericScalar)
    filtered_list = graphene.List(generic.GenericScalar)

    def resolve_id(self, info):
        return self.id or None
    def resolve_name(self, info):
        return self.name or None
    def resolve_display_name(self, info):
        return self.display_name or None
    
    def resolve_display_type(self, info):
        return self.display_type or None
    
    #def resolve_product_create_mode(self, info):
    #    return self.create_product or None

    def resolve_filter_visibility(self, info):
        return self.visibility or None

    def resolve_list(self, info):
        return self.list or None
    def resolve_filtered_list(self, info):
        return self.list or None
    
    def resolve_min(self, info):
        if self.scalar_type == "integer" and self.min != None:
            return int(self.min) or None
        return self.min or None
    def resolve_filtered_min(self, info):
        if self.scalar_type == "integer" and self.filtered_min != None:
            return int(self.filtered_min) or None
        return self.filtered_min or None
    
    def resolve_max(self, info):
        if self.scalar_type == "integer" and self.max != None:
            return int(self.max) or None
        return self.max or None
    def resolve_filtered_max(self, info):
        if self.scalar_type == "integer" and self.filtered_max != None:
            return int(self.filtered_max) or None
        return self.filtered_max or None
    

class AttributeValue(ObjectType):
    id = graphene.String(required=True)
    value = graphene.String()
    type = graphene.String()
    display_type = graphene.String()
    html_color = graphene.String()
    search = graphene.String()
    price_extra = graphene.Float(description='Not use in the return Attributes List of the Products Query')
    attribute = graphene.Field(lambda: Attribute)

    def resolve_id(self, info):
        return self.id or None
    def resolve_value(self, info):
        return self.value or None
    def resolve_type(self, info):
        return self.type or None
    def resolve_display_type(self, info):
        return self.display_type or None
    def resolve_html_color(self, info):
        return self.html_color or None
    def resolve_price_extra(self, info):
        return 0.0 or None

    def resolve_search(self, info):
        #print("(Rich) AttributeValue resolve search")
        return '{}-{}'.format(self.id, self.id) or None

    def resolve_attribute(self, info):
        #print("(Rich) Attribute resolve search")
        return self.attribute or None

class Attribute(ObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    display_name = graphene.String()


    # scalar, range, list, ...
    struct_type = graphene.String()

    # string, integer, bool, ..
    scalar_type = graphene.String()

    # textbox, radio, dropdown, multi-radio, selection, multi-selection, checkbox, multi-checkbox
    # range, price, color, checkbox
    display_type = graphene.String()

    filter_visibility = FilterVisibility()

    # struct_type: scalar or range
    min = graphene.String()
    max = graphene.String()

    # struct_type: select or multi-select
    values = graphene.List(graphene.String)

    def resolve_id(self, info):
        return self.id or None
    def resolve_name(self, info):
        return self.name or None
    def resolve_display_name(self, info):
        return self.display_name or None
    
    def resolve_display_type(self, info):
        return self.display_type or None
    
    #def resolve_product_create_mode(self, info):
    #    return self.create_product or None

    def resolve_filter_visibility(self, info):
        return self.visibility or None

    def resolve_values(self, info):
        return self.values or None
    
    def resolve_min(self, info):
        #if self.scalar_type == "integer":
        #    print('return a min of int')
        #    return int(self.min) or None
        return self.min or None
    
    def resolve_max(self, info):
        #if self.scalar_type == "integer":
        #    print('return a max of int')
        #    return int(self.max) or None
        return self.max or None




class Facet(ObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    display_name = graphene.String()


    # scalar, range, list, ...
    struct_type = graphene.String()

    # string, integer, bool, ..
    scalar_type = graphene.String()

    # textbox, radio, dropdown, multi-radio, selection, multi-selection, checkbox, multi-checkbox
    # range, price, color, checkbox
    display_type = graphene.String()

    filter_visibility = FilterVisibility()

    # struct_type: scalar or range
    min = generic.GenericScalar()
    filtered_min = generic.GenericScalar()

    max = generic.GenericScalar()
    filtered_max = generic.GenericScalar()

    # struct_type: select or multi-select
    list = graphene.List(generic.GenericScalar)
    filtered_list = graphene.List(generic.GenericScalar)

    def resolve_id(self, info):
        return self.id or None
    def resolve_name(self, info):
        return self.name or None
    def resolve_display_name(self, info):
        return self.display_name or None
    
    def resolve_display_type(self, info):
        return self.display_type or None
    
    #def resolve_product_create_mode(self, info):
    #    return self.create_product or None

    def resolve_filter_visibility(self, info):
        return self.visibility or None

    def resolve_list(self, info):
        return self.list or None
    def resolve_filtered_list(self, info):
        return self.list or None
    
    def resolve_min(self, info):
        if self.scalar_type == "integer" and self.min != None:
            return int(self.min) or None
        return self.min or None
    def resolve_filtered_min(self, info):
        if self.scalar_type == "integer" and self.filtered_min != None:
            return int(self.filtered_min) or None
        return self.filtered_min or None
    
    def resolve_max(self, info):
        if self.scalar_type == "integer" and self.max != None:
            return int(self.max) or None
        return self.max or None
    def resolve_filtered_max(self, info):
        if self.scalar_type == "integer" and self.filtered_max != None:
            return int(self.filtered_max) or None
        return self.filtered_max or None
    
from typing import List
from typing import Any
from dataclasses import dataclass
import json

from graphene.types import generic

from meta_schema import MetaSchema, MetaProperties, MetaProperty, MetaStruct

@dataclass
class AttributeTypeProperties (MetaProperties):
    def __init__(self):

        self.name = MetaProperty(type="string", description="Name of trait.")
        self.display_name = MetaProperty(type="string", description="Display name of trait.")
        self.struct_type = MetaProperty(type="string", description="scalar, list, range, ...")
        self.scalar_type = MetaProperty(type="string", description="string, integer, boolean, number, ...")
        self.min = MetaProperty(type=["string", "integer", "number", "boolean"], description="min for trait.")      
        self.max = MetaProperty(type=["string", "integer", "number", "boolean"], description="min for trait.")  
        #self.list = MetaProperty(type=["string", "integer", "number", "boolean"], description="trait list")

        #properties = MetaProperty(type=["string", "integer", "number", "boolean"], description="list value")
        #self.list = MetaStruct(type="array", properties=properties)  
    
    name: MetaProperty
    display_type: MetaProperty
    value: MetaProperty

    def from_dict(obj: Any) -> 'AttributeTypeProperties':
        _name = MetaProperty.from_dict(obj.get("name"))
        _display_name = MetaProperty.from_dict(obj.get("display_type"))
        return AttributeTypeProperties(_name, _display_name)
from typing import List
from typing import Any
from dataclasses import dataclass
import json

from graphene.types import generic

from meta_schema import MetaSchema, MetaProperties, MetaProperty, MetaStruct
from attribute_schema import AttributeTypeProperties

        
@dataclass
class ProductProperties (MetaProperties):
    def __init__(self):

        self.name = MetaProperty(type="string", description="Identifies the asset to which this token represents.")
        self.description = MetaProperty(type="string", description="Description of the asset to which this token represents.")      
        self.image = MetaProperty(type="string", description="Header image for product")

        properties = AttributeTypeProperties()
        required = ["name", "description"]
        self.attribute_types = MetaStruct(type="array", properties=properties, required=required)
        
        

    name: MetaProperty
    description: MetaProperty
    image: MetaProperty

    attribute_types = MetaStruct


    def from_dict(obj: Any) -> 'ProductProperties':
        _name = MetaProperty.from_dict(obj.get("name"))
        _description = MetaProperty.from_dict(obj.get("description"))
        _image = MetaProperty.from_dict(obj.get("image"))
        return ProductProperties(_name, _description, _image)
    


@dataclass
class ProductMetadataSchema (MetaSchema):
    def __init__(self, schema=None, title=None, type=None, version=None, properties=None, required=None):
        MetaSchema.__init__(self, schema, title, type, version, properties, required)
        
        if properties == None:
            self.properties = ProductProperties()

        if required == None:
            self.required =[
                "name",
                "image",
                "description"
            ]




    


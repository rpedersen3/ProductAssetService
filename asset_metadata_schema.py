from typing import List
from typing import Any
from dataclasses import dataclass
import json

from meta_schema import MetaSchema, MetaProperties, MetaStruct, MetaProperty
    
@dataclass
class AssetAttributeProperties (MetaProperties):
    def __init__(self):

        self.name = MetaProperty(type="string", description="Name of trait.")
        self.display_type = MetaProperty(type="string", description="Sets the representation of the value of the trait.")
        self.value = MetaProperty(type=["string", "integer", "number", "boolean"], description="Value for trait.")      
        
    name: MetaProperty
    display_type: MetaProperty
    value: MetaProperty

    def from_dict(obj: Any) -> 'AssetProperties':
        _name = MetaProperty.from_dict(obj.get("name"))
        _display_type = MetaProperty.from_dict(obj.get("display_type"))
        _value = MetaProperty.from_dict(obj.get("value"))
        return AssetAttributeProperties(_name, _display_type, _value)
    


@dataclass
class AssetProperties (MetaProperties):
    def __init__(self):

        self.name = MetaProperty(type="string", description="Name of Asset")
        self.price = MetaProperty(type="number", description="Price of land")
        self.image = MetaProperty(type="string", description="Land Image")      
       
        properties = AssetAttributeProperties()
        required = ["name", "value"]
        self.attributes = MetaStruct(type="array", properties=properties, required=required)

    name: MetaProperty
    price: MetaProperty
    image: MetaProperty
    attributes = MetaStruct

    def from_dict(obj: Any) -> 'AssetProperties':
        _name = MetaProperty.from_dict(obj.get("name"))
        _price = MetaProperty.from_dict(obj.get("price"))
        _image = MetaProperty.from_dict(obj.get("image"))
        return AssetProperties(_name, _price, _image)
    


@dataclass
class AssetMetadataSchema (MetaSchema):
    def __init__(self, schema=None, title=None, type=None, version=None, properties=None, required=None):
        MetaSchema.__init__(self, schema, title, type, version, properties, required)
        
        if title == None:
            self.title = "Asset Metadata Schema"

        if properties == None:
            self.properties = AssetProperties()

        if required == None:
            self.required =[
                "name"
            ]


    


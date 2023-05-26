import json
from json import JSONEncoder, JSONDecoder

from typing import List
from typing import Any
from dataclasses import dataclass
import json

@dataclass
class AssetAttributeMetadata:
    def __init__(self, id, type, display_name=None, display_type=None, value=None):
        self.id = id
        self.type = type
        self.display_name = display_name
        self.display_type = display_type
        self.value = value

    id: str
    type: str
    display_name: str
    display_type: str
    value: str


    @staticmethod
    def from_dict(obj: Any) -> 'AssetAttributeMetadata':
        _id = str(obj.get("id"))
        _type = str(obj.get("type"))
        _display_name = str(obj.get("display_name"))
        _display_type = str(obj.get("display_type"))
        _value = obj.get("value")

        return AssetAttributeMetadata(_id, _type, _display_name, _display_type, _value)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        return jsn

@dataclass  
class AssetMetadata(object):
    def __init__(self, name, display_name, description, image, price, attributes):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.image = image
        self.price = price
        self.attributes = attributes

    name: str
    display_name: str
    description: str
    image: str
    price: float
    
    attributes: List[AssetAttributeMetadata]

    @staticmethod
    def from_dict(obj: Any) -> 'AssetMetadata':
        _name = str(obj.get("name"))
        _display_name = str(obj.get("display_name"))
        _image = str(obj.get("image"))
        _description = str(obj.get("description"))
        _price = float(obj.get("price"))

        _attributes = obj.get("attributes")

        return AssetMetadata(_name, _display_name, _description, _image, _price, _attributes)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        return jsn




 
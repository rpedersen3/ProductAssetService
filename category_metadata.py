import json
from json import JSONEncoder, JSONDecoder

from typing import List
from typing import Any
from dataclasses import dataclass
import json

from attribute_type_metadata import AttributeTypeMetadata
from product_metadata import ProductMetadata



@dataclass  
class CategoryMetadata(object):
    def __init__(self, name, display_name, description, image, products, attribute_types):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.image = image
        self.products = products
        self.attribute_types = attribute_types

    name: str
    display_name: str
    description: str
    image: str
    
    products: List[ProductMetadata]
    attribute_types: List[AttributeTypeMetadata]

    @staticmethod
    def from_dict(obj: Any) -> 'CategoryMetadata':
        _name = str(obj.get("name"))
        _display_name = str(obj.get("display_name"))
        _image = str(obj.get("image"))
        _description = str(obj.get("description"))

        _products = obj.get("products")
        _attribute_types = obj.get("attribute_types")

        return CategoryMetadata(_name, _display_name, _description, _image, _products, _attribute_types)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        return jsn




 
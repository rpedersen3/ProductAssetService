from typing import List
from typing import Any
from dataclasses import dataclass
import json

from attribute_type_metadata import AttributeTypeMetadata

@dataclass
class ProductMetadata:
    def __init__(self, id, name, description=None, image=None, attributeTypes=None, facets=None):
        self.id = id
        self.name = name
        self.description = description
        self.image = image
        self.attributeTypes = attributeTypes


    id: str
    name: str
    description: str
    image: str

    attributeTypes: List[AttributeTypeMetadata]



    @staticmethod
    def from_dict(obj: Any) -> 'ProductMetadata':
        _id = str(obj.get("id"))
        _name = str(obj.get("name"))
        _description = str(obj.get("description"))
        _image = str(obj.get("image"))

        return ProductMetadata(_id, _name, _description, _image)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        return jsn

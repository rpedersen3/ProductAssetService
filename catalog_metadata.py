from typing import List
from typing import Any
from dataclasses import dataclass
import json

from attribute_type_metadata import AttributeTypeMetadata


@dataclass
class CatalogMetadata:
    def __init__(self, name, description=None, image=None, attribute_types=None, facets=None):
        self.name = name
        self.description = description
        self.image = image
        self.attribute_types = attribute_types


    name: str
    description: str
    image: str
    struct_type: str
    scalar_type: str

    attribute_types: List[AttributeTypeMetadata]



    @staticmethod
    def from_dict(obj: Any) -> 'CatalogMetadata':
        _name = str(obj.get("name"))
        _description = str(obj.get("description"))
        _image = str(obj.get("image"))

        return CatalogMetadata(_name, _description, _image)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        return jsn

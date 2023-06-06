import json
from json import JSONEncoder, JSONDecoder

from typing import List
from typing import Any
from dataclasses import dataclass
import json

from attribute_metadata import AttributeMetadata

@dataclass  
class ItemMetadata(object):
    def __init__(self, name, display_name=None, description=None, image=None, attributes=None):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.image = image
        self.attributes = attributes

    name: str
    display_name: str
    description: str
    image: str
    
    attributes: List[AttributeMetadata]

    @staticmethod
    def from_dict(obj: Any) -> 'ItemMetadata':
        _name = str(obj.get("name"))
        _display_name = str(obj.get("display_name"))
        _image = str(obj.get("image"))
        _description = str(obj.get("description"))

        _attributes = obj.get("attributes")

        return ItemMetadata(_name, _display_name, _description, _image, _attributes)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        return jsn
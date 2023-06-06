import json
from json import JSONEncoder, JSONDecoder

from typing import List
from typing import Any
from dataclasses import dataclass
import json

from attribute_type_metadata import AttributeTypeMetadata

@dataclass
class CollectionMetadata:
    def __init__(self, id, name, type, description=None, attributeTypes=None):
        self.id = id
        self.name = name
        self.type = type
        self.description = description
        self.attributeTypes = attributeTypes

    id: str
    name: str
    type: str
    description: str

    attributeTypes: List[AttributeTypeMetadata]


    @staticmethod
    def from_dict(obj: Any) -> 'CollectionMetadata':
        _id = str(obj.get("id"))
        _name = str(obj.get("name"))
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))

        return CollectionMetadata(_id, _name, _type, _description)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        return jsn




 
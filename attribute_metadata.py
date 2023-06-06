import json
from json import JSONEncoder, JSONDecoder

from typing import List
from typing import Any
from dataclasses import dataclass
import json

@dataclass
class AttributeMetadata:
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
    def from_dict(obj: Any) -> 'AttributeMetadata':
        _id = str(obj.get("id"))
        _type = str(obj.get("type"))
        _display_name = str(obj.get("display_name"))
        _display_type = str(obj.get("display_type"))
        _value = obj.get("value")

        return AttributeMetadata(_id, _type, _display_name, _display_type, _value)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        return jsn



 
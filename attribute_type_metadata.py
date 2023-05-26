from typing import List
from typing import Any
from dataclasses import dataclass
import json


@dataclass
class AttributeTypeMetadata:
    def __init__(self, name, display_name, description=None, struct_type=None, scalar_type=None, min=None, max=None, list=None):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.struct_type = struct_type
        self.scalar_type = scalar_type
        self.min = min
        self.max = max
        self.list = list

    name: str
    display_name: str
    description: float
    struct_type: str
    scalar_type: str
    min: object
    max: object
    list: List

    @staticmethod
    def from_dict(obj: Any) -> 'AttributeTypeMetadata':
        _name = str(obj.get("name"))
        _display_name = str(obj.get("display_name"))
        _description = str(obj.get("description"))
        _struct_type = str(obj.get("struct_type"))
        _scalar_type = str(obj.get("scalar_type"))
        _min = obj.get("min")
        _max = obj.get("max")
        _list = obj.get("list")

        return AttributeTypeMetadata(_name, _display_name, _description, _struct_type, _scalar_type, _min, _max, _list)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        return jsn


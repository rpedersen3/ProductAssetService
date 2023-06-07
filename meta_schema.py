from typing import List
from typing import Any
from dataclasses import dataclass
import json

from abc import ABC, abstractmethod

@dataclass
class MetaProperty:
    def __init__(self, type, description=None, properties=None, additional_properties=None, required=None):
        self.type = type
        self.description = description
        self.properties = properties
        self.additional_properties = additional_properties
        self.required = required

    type: str
    description: str
    properties: object
    additional_properties: bool
    required: List[str]

    @staticmethod
    def from_dict(obj: Any) -> 'MetaProperty':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        _properties = MetaProperties.from_dict(obj.get("properties"))

        return MetaProperty(_type, _description, _properties)
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=4)
    
@dataclass
class MetaStruct:
    def __init__(self, type, properties=None, required=None):

        self.type = type
        self.items = MetaProperty(type="object", properties=properties)
        self.required = required


    type: str
    items: MetaProperty
    required: List[str]

    @staticmethod
    def from_dict(obj: Any) -> 'MetaProperty':
        _type = str(obj.get("type"))
        _items = MetaProperty.from_dict(obj.get("items"))
        
        return MetaProperty(_type, _items)
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=4)
    
@dataclass
class MetaProperties(ABC):

    @abstractmethod
    def from_dict(obj: Any) -> 'MetaProperties':
        pass
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=4)
    
@dataclass
class MetaSchema:
    def __init__(self, schema=None, title=None, type=None, version=None, properties=None, required=None):
        if schema != None:
            self.schema = schema
        else:
            self.schema = "http://json-schema.org/draft-07/schema#"

        if title != None:  
            self.title = title
        else:
            self.title = "Metadata Schema"

        if type != None: 
            self.type = type  
        else: 
            self.type = "object"
 
        if version != None:
            self.version = version
        else:
            self.version = "0.0.1"

        if properties != None:
            self.properties = properties

        if required != None:
            self.required = required


    schema: str 
    version: str    
    title: str
    type: str
    properties: MetaProperties
    additionalProperties: bool
    required: List[str]

    @staticmethod
    def from_dict(obj: Any) -> 'MetaSchema':
        _title = str(obj.get("title"))
        _type = str(obj.get("type"))
        _version = str(obj.get("version"))
        _schema = str(obj.get("$schema"))
        _properties = MetaProperties.from_dict(obj.get("properties"))
        _required = [str.from_dict(y) for y in obj.get("required")]
        
        return MetaSchema(schema=_schema, title=_title, type=_type, version=_version, properties=_properties, required=_required)
    
    def toJSON(self):
        jsn = json.dumps(self,
                      default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                      indent=4,
                      sort_keys=False,
                      allow_nan=False)
        jsn = jsn.replace("\"schema\":", "\"$schema\":")
        return jsn

    
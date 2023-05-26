import graphene
from graphene import ObjectType

FilterVisibility = graphene.Enum('FilterVisibility', [('Visible', 'visible'), ('Hidden', 'hidden')])

class SortEnum(graphene.Enum):
    ASC = 'ASC'
    DESC = 'DESC'
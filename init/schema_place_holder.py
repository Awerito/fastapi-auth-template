from pydantic import BaseModel, Field

from src.schemas.id import Id
#Imports#


class #SchemaName#(BaseModel):
    id: Id = Field(..., alias="_id")
# SCHEMACOLUMNS


class #SchemaName#Create(BaseModel):
# CREATECOLUMNS
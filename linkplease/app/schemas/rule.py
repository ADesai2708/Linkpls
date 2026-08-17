from pydantic import BaseModel, Field


class RuleCreate(BaseModel):
    keyword: str = Field(min_length=1, max_length=100)
    dm_message: str = Field(min_length=1)


class RuleResponse(BaseModel):
    rule_id: str
    keyword: str
    dm_message: str
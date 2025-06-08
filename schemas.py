from typing import List, Optional
from pydantic import BaseModel

class Formatting(BaseModel):
    type: Optional[str]
    currency_symbol: Optional[str]
    decimal_places: Optional[int]

class FilterCondition(BaseModel):
    field: str
    condition: str

class CustomColors(BaseModel):
    text_color: Optional[str]
    background_color: Optional[str]
    line_color: Optional[str]

class TooltipCustomization(BaseModel):
    enable: bool
    fields: List[str]

class Visual(BaseModel):
    visual_type: str
    title: str
    field: Optional[str]
    aggregation: Optional[str]
    formatting: Optional[Formatting]
    filters: List[FilterCondition]
    custom_colors: Optional[CustomColors]
    tooltip_customization: Optional[TooltipCustomization]

class DashboardRequest(BaseModel):
    platform: str
    dashboard_name: str
    visuals: List[Visual]
from pydantic import BaseModel, Field
from typing import Dict, Optional


class ProviderConfig(BaseModel):
    name: str = Field(..., description="Tên hiển thị (VD: Giá Vàng SJC)")
    command: str = Field(..., description="Lệnh bot (VD: vang)")
    url: str = Field(..., description="Link API")
    method: str = Field("GET", description="Phương thức HTTP")
    headers: Dict[str, str] = Field(default_factory=dict)
    params: Dict[str, str] = Field(default_factory=dict)
    payload: Optional[Dict] = None
    provider_type: str = Field("json", description="Loại provider: json, scraper, petrolimex")
    data_path: str = Field(..., description="Đường dẫn tới mảng dữ liệu hoặc object chính")
    fields: Dict[str, str] = Field(..., description="Mapping nhãn hiển thị và tên trường API")

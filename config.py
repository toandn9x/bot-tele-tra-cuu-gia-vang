from models import ProviderConfig
from typing import List

# Cấu hình các dịch vụ tra cứu tại đây
SERVICES: List[ProviderConfig] = [
    ProviderConfig(
        name="Giá Vàng Hôm Nay",
        command="gold",
        url="https://giavang.now/api/prices",
        data_path="prices",
        fields={
            "Loại": "name",
            "Mua vào": "buy",
            "Bán ra": "sell"
        }
    ),
    ProviderConfig(
        name="Giá Xăng Dầu",
        command="xang",
        provider_type="petrolimex",
        url="https://portals.petrolimex.com.vn/~apis/portals/cms.item/search",
        data_path="Objects",
        fields={
            "Loại xăng": "Title",
            "Vùng 1": "Zone1Price",
            "Vùng 2": "Zone2Price"
        }
    ),
    ProviderConfig(
        name="Tỷ giá USD (VND)",
        command="usd",
        url="https://api.exchangerate-api.com/v4/latest/USD",
        data_path="rates",
        fields={
            "VND": "VND",
            "EUR": "EUR",
            "JPY": "JPY"
        }
    )
]

# Token Bot (Cần điền vào đây)
TELEGRAM_BOT_TOKEN = ""

# Thông tin tác giả và Donate
AUTHOR_INFO = "👨‍💻 **Tác giả:** Toandn"
DONATE_INFO = "💸 **Ủng hộ tác giả:** Ngân hàng: BIDV - 1222172532"

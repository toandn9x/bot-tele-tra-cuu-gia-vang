import httpx
import logging
import json
import base64
import hashlib
import random
from abc import ABC, abstractmethod
from typing import Any, Dict
from bs4 import BeautifulSoup
from models import ProviderConfig

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    async def fetch_data(self) -> str:
        pass

    def _build_table(self, labels: list[str], rows: list[list[str]]) -> str:
        """Tạo bảng monospace dùng chung cho mọi provider."""
        header_text = f"📊 *{self.config.name.upper()}*\n"

        n = len(labels)
        if n == 1:
            row_format = "{:<20}"
        elif n == 2:
            row_format = "{:<20} {:>10}"
        elif n == 3:
            row_format = "{:<18} {:>9} {:>9}"
        else:
            row_format = "{:<12}" + " {:>8}" * (n - 1)

        short_labels = [l[:12] for l in labels]
        table = "```\n"
        table += row_format.format(*short_labels) + "\n"
        table += "-" * 36 + "\n"

        for values in rows:
            try:
                table += row_format.format(*values) + "\n"
            except (IndexError, TypeError):
                table += " | ".join(values) + "\n"

        table += "```"
        return header_text + table

    @staticmethod
    def _format_number(val) -> str:
        if isinstance(val, (int, float)):
            if val >= 1_000_000:
                return f"{val / 1_000_000:.1f}M"
            if val >= 1_000:
                return f"{val:,.0f}"
        return str(val)[:15]


class JSONProvider(BaseProvider):
    async def fetch_data(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                if self.config.method.upper() == "POST":
                    response = await client.post(
                        self.config.url,
                        json=self.config.payload,
                        headers=self.config.headers,
                        params=self.config.params
                    )
                else:
                    response = await client.get(
                        self.config.url,
                        headers=self.config.headers,
                        params=self.config.params
                    )

                response.raise_for_status()
                return self._parse_json(response.json())
        except Exception as e:
            logger.error(f"Error fetching data from {self.config.name}: {e}")
            return f"⚠️ Lỗi khi lấy dữ liệu {self.config.name}: {str(e)}"

    def _parse_json(self, data: Any) -> str:
        # Điều hướng sâu vào JSON theo data_path
        current = data
        for part in self.config.data_path.split('.'):
            if not part or not current:
                continue

            if part.startswith('[') and part.endswith(']'):
                idx = int(part[1:-1])
                if isinstance(current, list) and len(current) > idx:
                    current = current[idx]
                continue

            if isinstance(current, list):
                return f"❌ Cấu trúc JSON không khớp tại: {part}"
            current = current.get(part)

        # Chuẩn bị dữ liệu hiển thị
        if isinstance(current, list):
            items_data = current[:15]
        elif isinstance(current, dict):
            if not current:
                return f"⚠️ Không có dữ liệu cho {self.config.name}."
            first_val = next(iter(current.values()))
            items_data = list(current.values())[:20] if isinstance(first_val, dict) else [current]
        else:
            return f"✅ Dữ liệu {self.config.name}: {current}"

        if not items_data:
            return f"⚠️ Không có dữ liệu cho {self.config.name}."

        labels = list(self.config.fields.keys())
        rows = []
        for item in items_data:
            row = [self._format_number(item.get(field, "-")) for field in self.config.fields.values()]
            rows.append(row)

        return self._build_table(labels, rows)


class PetrolimexProvider(BaseProvider):
    """Provider gọi API nội bộ của Petrolimex để lấy giá xăng dầu."""

    API_URL = "https://portals.petrolimex.com.vn/~apis/portals/cms.item/search"
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    FILTER_PAYLOAD = {
        "FilterBy": {
            "And": [
                {"SystemID": {"Equals": "6783dc1271ff449e95b74a9520964169"}},
                {"RepositoryID": {"Equals": "a95451e23b474fe5886bfb7cf843f53c"}},
                {"RepositoryEntityID": {"Equals": "3801378fe1e045b1afa10de7c5776124"}},
                {"Status": {"Equals": "Published"}}
            ]
        },
        "SortBy": {"OrderIndex": "Ascending"},
        "Pagination": {"TotalRecords": -1, "TotalPages": 0, "PageSize": 0, "PageNumber": 0}
    }

    @staticmethod
    def _b64url(text: str) -> str:
        b64 = base64.b64encode(text.encode()).decode()
        return b64.rstrip("=").replace("+", "-").replace("/", "_")

    def _build_url(self) -> str:
        x_request = self._b64url(json.dumps(self.FILTER_PAYLOAD, separators=(",", ":")))
        device_id = hashlib.md5((self.UA + str(random.random())).encode()).hexdigest() + "@portals"
        params = (
            f"x-request={x_request}"
            f"&x-device-id={self._b64url(device_id)}"
            f"&x-app-name={self._b64url('NGX Websites')}"
            f"&x-app-platform={self._b64url('Desktop PWA')}"
            f"&language=vi-VN"
        )
        return f"{self.API_URL}?{params}"

    async def fetch_data(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(self._build_url(), headers={
                    "User-Agent": self.UA,
                    "Origin": "https://www.petrolimex.com.vn",
                    "Referer": "https://www.petrolimex.com.vn/",
                })
                response.raise_for_status()
                items = response.json().get("Objects", [])
                return self._format_prices(items)
        except Exception as e:
            logger.error(f"Error fetching Petrolimex data: {e}")
            return f"⚠️ Lỗi khi lấy dữ liệu {self.config.name}: {str(e)}"

    def _format_prices(self, items: list) -> str:
        if not items:
            return f"⚠️ Không có dữ liệu cho {self.config.name}."

        items.sort(key=lambda x: x.get("DIsplayOrder", 99))

        labels = list(self.config.fields.keys())
        rows = []
        for item in items:
            title = item.get("Title", "-")[:18]
            z1 = item.get("Zone1Price", 0)
            z2 = item.get("Zone2Price", 0)
            rows.append([title, f"{z1:,.0f}" if z1 else "-", f"{z2:,.0f}" if z2 else "-"])

        return self._build_table(labels, rows)


class WebScraperProvider(BaseProvider):
    async def fetch_data(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(
                    self.config.url,
                    headers=self.config.headers or {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    params=self.config.params
                )
                response.raise_for_status()
                return self._parse_html(response.text)
        except Exception as e:
            logger.error(f"Error scraping data from {self.config.name}: {e}")
            return f"⚠️ Lỗi khi cào dữ liệu {self.config.name}: {str(e)}"

    def _parse_html(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.select_one('div.f-list table')
        if not table:
            return f"❌ Không tìm thấy bảng giá trên trang {self.config.name}"

        tbody = table.find('tbody')
        trs = tbody.find_all('tr') if tbody else table.find_all('tr')

        labels = list(self.config.fields.keys())
        field_keys = list(self.config.fields.values())
        rows = []
        for tr in trs:
            cols = tr.find_all('td')
            if len(cols) >= len(field_keys):
                row = [cols[i].text.strip()[:15] for i in range(len(field_keys))]
                rows.append(row)

        if not rows:
            return f"⚠️ Không có dữ liệu cho {self.config.name}."

        return self._build_table(labels, rows)


# Registry để map provider_type -> class
PROVIDER_REGISTRY: Dict[str, type[BaseProvider]] = {
    "json": JSONProvider,
    "petrolimex": PetrolimexProvider,
    "scraper": WebScraperProvider,
}

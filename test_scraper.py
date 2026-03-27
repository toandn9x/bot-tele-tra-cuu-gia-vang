import asyncio
from models import ProviderConfig
from providers import WebScraperProvider

sample_html = """
<div class="f-list" style="right: -199px;"><table><thead><tr>
        <th>Sản phẩm</th>
        <th>Vùng 1</th>
        <th><a href="https://www.petrolimex.com.vn/vung-2.html" target="_blank">Vùng 2</a></th>
        </tr></thead><tbody><tr><td>Xăng RON 95-V</td><td>24.730</td><td>25.220</td></tr><tr><td>Xăng RON 95-III</td><td>24.330</td><td>24.810</td></tr><tr><td>Xăng E10 RON 95-III</td><td>23.690</td><td>24.160</td></tr><tr><td>Xăng E5 RON 92-II</td><td>23.320</td><td>23.780</td></tr><tr><td>DO 0,001S-V</td><td>35.640</td><td>36.350</td></tr><tr><td>DO 0,05S-II</td><td>35.440</td><td>36.140</td></tr><tr><td>Dầu hỏa 2-K</td><td>35.380</td><td>36.080</td></tr></tbody></table><p class="f-info"><span>*đơn vị: VND</span>
            Giá của Petrolimex cập nhật lúc
            &nbsp;24:00 - 26/3/2026</p></div>
"""

config = ProviderConfig(
    name="Giá Xăng Dầu",
    command="xang",
    provider_type="scraper",
    url="https://www.petrolimex.com.vn/",
    data_path="",
    fields={
        "Loại xăng": "name",
        "Vùng 1": "region1",
        "Vùng 2": "region2"
    }
)

provider = WebScraperProvider(config)
result = provider._parse_html(sample_html)
print(result)

# Test real fetch
async def main():
    res = await provider.fetch_data()
    print("= REAL FETCH =")
    print(res)

if __name__ == '__main__':
    asyncio.run(main())

import urllib.request
from bs4 import BeautifulSoup
import re

url = "https://www.petrolimex.com.vn/ndi/thong-cao-bao-chi/petrolimex-dieu-chinh-gia-xang-dau-tu-24-gio-00-phut-ngay-26-3-2026.html"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get the main content div if any
        # Usually it's in a div with class 'content' or 'detail'
        main = soup.find('div', class_=re.compile('content|detail|post', re.IGNORECASE))
        if not main:
            main = soup.body
            
        print(main.text[:1500].replace('\n\n', '\n'))
        
except Exception as e:
    print(f"Error: {e}")

import urllib.request
from bs4 import BeautifulSoup
import json
import re

url = "https://www.petrolimex.com.vn/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        
        # The user said the table is in <div class="f-list" style="right: -199px;"><table>
        # Let's try to find div.f-list
        f_list = soup.find('div', class_='f-list')
        if f_list:
            print("Found div.f-list")
            table = f_list.find('table')
            if table:
                rows = table.find_all('tr')
                data = []
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    cols = [ele.text.strip().replace('\n', ' ') for ele in cols]
                    if cols:
                        data.append(cols)
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print("No table found inside div.f-list")
        else:
            print("No div.f-list found on the home page")
            # Print some of the HTML to see where we are
            print(html[:1000].decode('utf-8'))
            
except Exception as e:
    print(f"Error: {e}")

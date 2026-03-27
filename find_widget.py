import urllib.request
from bs4 import BeautifulSoup
import re

url = "https://www.petrolimex.com.vn/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for iframes
        for iframe in soup.find_all('iframe'):
            print(f"Iframe found: {iframe.get('src')}")
            
        # Look for scripts that might load data
        for script in soup.find_all('script'):
            src = script.get('src')
            if src:
                print(f"Script: {src}")
            elif script.string and 'f-list' in script.string:
                print("Found f-list in inline script")
                print(script.string[:500])
except Exception as e:
    print(f"Error: {e}")

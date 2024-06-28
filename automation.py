import aiohttp
import asyncio
import re
import random

from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class ProxyFinder:
    def __init__(self):
        self.proxy_sources = [
            'https://www.proxy-list.download/api/v1/get?type=https',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://www.proxy-list.download/api/v1/get?type=socks4',
            'https://www.proxy-list.download/api/v1/get?type=socks5',
            'https://www.sslproxies.org/',
            'https://www.socks-proxy.net/',
            'https://free-proxy-list.net/',
            'https://www.proxynova.com/proxy-server-list/',
            'https://www.proxysource.org/',
        ]
        self.test_url = 'http://httpbin.org/ip'
        self.proxies = set()
        self.working_proxies = []

    async def fetch_proxies(self, session, url):
        tries = 3
        for attempt in range(tries):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        # Extract IP:Port combinations using regex
                        proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', text)
                        self.proxies.update(proxies)
                        return
            except:
                pass

    async def check_proxy(self, session, proxy):
        try:
            proxy_url = f'http://{proxy}'
            async with session.get(self.test_url, proxy=proxy_url, timeout=10) as response:
                if response.status == 200:
                    self.working_proxies.append(proxy)
        except:
            pass

    async def find_proxies(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_proxies(session, url) for url in self.proxy_sources]
            await asyncio.gather(*tasks)

    async def check_proxies(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_proxy(session, proxy) for proxy in self.proxies]
            await asyncio.gather(*tasks)

    def remove_duplicates(self):
        self.working_proxies = list(set(self.working_proxies))

    async def run(self):
        await self.find_proxies()
        await self.check_proxies()
        self.remove_duplicates()
        print(f'Found {len(self.working_proxies)} working proxies:')
        for proxy in self.working_proxies:
            print(proxy)

# Use ProxyFinder to get a working proxy
async def get_working_proxy():
    proxy_finder = ProxyFinder()
    await proxy_finder.run()
    if proxy_finder.working_proxies:
        return random.choice(proxy_finder.working_proxies)
    else:
        return None

async def main():
    proxy_ip = await get_working_proxy()
    if proxy_ip:
        # Set the proxy details
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = proxy_ip
        proxy.ssl_proxy = proxy_ip

        # Configure options for Brave
        brave_path = '/usr/bin/brave-browser'  # Update this path if needed
        options = Options()
        options.binary_location = brave_path

        # Set proxy with Selenium options
        options.add_argument(f"--proxy-server=http://{proxy_ip}")

        # Initialize the WebDriver with the specified options
        service = Service('/usr/local/bin/chromedriver')  # Update this path to your ChromeDriver location
        driver = webdriver.Chrome(service=service, options=options)

        # Open the specified URL
        driver.get("https://www.instagram.com/accounts/emailsignup/")   
    else:
        print("No working proxy found. Retrying...")
        await main()

if __name__ == '__main__':
    asyncio.run(main())

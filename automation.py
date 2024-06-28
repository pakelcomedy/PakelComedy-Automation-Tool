import aiohttp
import asyncio
import re
import random
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException

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
                        proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', text)
                        self.proxies.update(proxies)
                        return
            except Exception as e:
                print(f"Error fetching proxies from {url}: {e}")

    async def check_proxy(self, session, proxy):
        try:
            proxy_url = f'http://{proxy}'
            async with session.get(self.test_url, proxy=proxy_url, timeout=10) as response:
                if response.status == 200:
                    self.working_proxies.append(proxy)
        except Exception as e:
            print(f"Proxy {proxy} failed: {e}")

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

async def get_working_proxy(proxy_finder):
    await proxy_finder.run()
    if proxy_finder.working_proxies:
        return random.choice(proxy_finder.working_proxies)
    else:
        return None

async def setup_selenium(proxy_ip):
    driver = None
    try:
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = proxy_ip
        proxy.ssl_proxy = proxy_ip

        brave_path = '/usr/bin/brave-browser'
        options = Options()
        options.binary_location = brave_path
        options.add_argument(f"--proxy-server=http://{proxy_ip}")

        service = Service('/usr/local/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(15)  # Set a page load timeout
        driver.get("https://www.instagram.com/accounts/emailsignup/")

        # Check for privacy error by verifying page title or specific elements
        if "Privacy error" in driver.title:
            raise Exception("Privacy error encountered")

        return driver
    except TimeoutException as e:
        if driver:
            driver.quit()
        print(f"Page load timed out with proxy {proxy_ip}: {e}")
        return None
    except WebDriverException as e:
        if driver:
            driver.quit()
        print(f"WebDriver error with proxy {proxy_ip}: {e}")
        return None
    except Exception as e:
        if driver:
            driver.quit()
        print(f"Error setting up Selenium with proxy {proxy_ip}: {e}")
        return None

async def main():
    proxy_finder = ProxyFinder()
    while True:
        proxy_ip = await get_working_proxy(proxy_finder)
        if proxy_ip:
            print(f"Using proxy: {proxy_ip}")
            driver = await setup_selenium(proxy_ip)
            if driver:
                try:
                    await asyncio.sleep(15)  # Wait for some time for page interaction
                    title = driver.title  # Perform some action to verify page loaded successfully
                    if "Privacy error" in title:
                        raise Exception("Privacy error encountered")
                    print(f"Successfully connected! Title: {title}")
                    break
                except Exception as e:
                    print(f"Error interacting with page: {e}")
                    driver.quit()
                    print("Page load error, retrying with a new proxy...")
            else:
                print("Failed to connect, retrying with a new proxy...")
        else:
            print("No working proxy found. Retrying...")
            await asyncio.sleep(5)  # Wait before retrying

if __name__ == '__main__':
    asyncio.run(main())

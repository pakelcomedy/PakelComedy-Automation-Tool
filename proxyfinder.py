import aiohttp
import asyncio
import re

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

if __name__ == '__main__':
    proxy_finder = ProxyFinder()
    asyncio.run(proxy_finder.run())

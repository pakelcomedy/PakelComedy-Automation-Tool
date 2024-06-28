import aiohttp
import asyncio

class ProxyFinder:
    def __init__(self):
        self.proxy_sources = [
            'https://www.proxy-list.download/api/v1/get?type=https',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://www.proxy-list.download/api/v1/get?type=socks4',
            'https://www.proxy-list.download/api/v1/get?type=socks5',
            'https://www.sslproxies.org/',
            'https://www.socks-proxy.net/',
            'https://www.proxy-daily.com/',
            'https://free-proxy-list.net/',
            'https://www.proxynova.com/proxy-server-list/',
            'https://www.proxyscan.io/',
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
                        proxies = text.split()
                        print(f"Fetched {len(proxies)} proxies from {url}")
                        self.proxies.update(proxies)
                        return
                    else:
                        print(f"Failed to fetch proxies from {url}, status code: {response.status}")
            except Exception as e:
                print(f"Error fetching proxies from {url}: {e}")
            print(f"Retrying {url} ({attempt + 1}/{tries})")
        print(f"Failed to fetch proxies from {url} after {tries} attempts")

    async def check_proxy(self, session, proxy):
        try:
            proxy_url = f'http://{proxy}'
            async with session.get(self.test_url, proxy=proxy_url, timeout=10) as response:
                if response.status == 200:
                    print(f'Working proxy: {proxy}')
                    self.working_proxies.append(proxy)
                else:
                    pass  # Optionally handle non-working proxies here
        except Exception as e:
            print(f"Error checking proxy {proxy}: {e}")

    async def find_proxies(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_proxies(session, url) for url in self.proxy_sources]
            await asyncio.gather(*tasks)
            print(f'Total proxies fetched: {len(self.proxies)}')

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
        print(f'Found {len(self.working_proxies)} working proxies.')
        if self.working_proxies:
            print("Working proxies:")
            for proxy in self.working_proxies:
                print(proxy)

if __name__ == '__main__':
    proxy_finder = ProxyFinder()
    asyncio.run(proxy_finder.run())

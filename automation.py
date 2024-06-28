from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set the proxy details
proxy_ip = "5.161.103.41:88"
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
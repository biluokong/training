import requests
from bs4 import BeautifulSoup

url = 'https://jd.com'

# 发送GET请并获取响应
response = requests.get(url)

# 根据文本的内容来推测它的编码方式，防止中文乱码输出。
response.encoding = response.apparent_encoding

# 使用BeautifulSoup解析响应文本
soup = BeautifulSoup(response.content, 'html.parser')

print(soup.text)


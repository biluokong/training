import re

my_str = 'http://j-d.m/?%&=dd'

print(re.search(r'http(s)?://([a-z0-9-]+.)+[a-z0-9-]{2,}(/?.*)?', my_str))


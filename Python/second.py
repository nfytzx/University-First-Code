import requests
url = 'https://m804.music.126.net/20251206235234/5449a35161060642b6c5d030619bd944/jdyyaac/obj/w5rDlsOJwrLDjj7CmsOj/625658\
36111/72bd/11fc/0687/60d16196835828ea89c62cc1f589d9d8.m4a?vuutv=4CoC/wEhNVvcL8OTrl9R9c+H7rcpvpwdYRfRWSTHIOnqPTOxlgHOpPL0zAtxkX+SkMDXgFjdTNG6nfzMTlT0AZgiYahkMcJ6rRa0UYBZfIE=&authSecret=0000019af446866c14870a3b19860993'
data = requests.get(url).content
print(data)
open('GOC.m4a','wb').write(data)

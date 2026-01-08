url = 'https://v1.kwaicdn.com/ksc2/6tfP1OjFQsCj67U-tsVPqiC9jO7QdouavvfHNHN_83zjJiTtDEcfrtPbLGYjM653UDEwC8yage6I1ZvPgRrk1Cmrsz7bwouy0XBd0bhw9FKhQjlJm2JnTrnGHs6uHSkQNFHFEA65h8xsLUY7pKvH-2nmJx7qTdRPqc5LqnutwaIFqnRMS6xyrSK_PRiCfGwt.mp4?pkey=AAWZ0e081_6GbogN0W5342NP_p9DBuVgryduvbjPc5sjpl8dlnh6QHxASwhLuCHJnnJubyCWi9DZ3_U-_jC6wS7bLLz9b0rK5OHNGhbhMsG1r-izf79LbypKZc0Sggas4hk&tag=1-1765035425-unknown-0-fwoqk1ndte-6ac0da6210d856f0&clientCacheKey=3x9s4j9hpbn353w_b.mp4&di=75166a77&bp=10004&kwai-not-alloc=40&tt=b&ss=vps'
import requests
data = requests.get(url).content
print(data)
open('111.mp4','wb').write(data)

from requests import get
msg = 'lemon candles are cool'
r = get(f"http://192.168.1.125:8777/?message='{msg}'")
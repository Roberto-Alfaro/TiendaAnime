import time
import urllib.request
import sys

url = 'http://127.0.0.1:8000/reporte/'
for i in range(15):
    try:
        r = urllib.request.urlopen(url, timeout=5)
        print('STATUS', r.getcode())
        data = r.read(2000)
        print(data.decode('utf-8', errors='replace'))
        sys.exit(0)
    except Exception as e:
        print(f'retry {i}:', e)
        time.sleep(1)
print('FAILED')
sys.exit(1)

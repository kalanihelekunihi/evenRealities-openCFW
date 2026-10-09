from pathlib import Path
import urllib.request,json,hashlib
O=Path(__file__).resolve().parent;O.joinpath('interface').mkdir(exist_ok=True)
commit='d1bf634023bf92d083ad0e32083987f67b4a64e6';url=f'https://raw.githubusercontent.com/Infineon/TARGET_CY8CKIT-040T/{commit}/system_cat2.h'
with urllib.request.urlopen(url) as r:data=r.read()
assert b'cy_israddress' in data and b'cy_delayFreqKhz' in data and b'__RAM_VECTOR_TABLE' in data
assert b'Apache-2.0' in data
(O/'interface/system_cat2.h').write_bytes(data)
(O/'acquisition.json').write_text(json.dumps({'repository':'https://github.com/Infineon/TARGET_CY8CKIT-040T.git','commit':commit,'url':url,'path':'interface/system_cat2.h','sha256':hashlib.sha256(data).hexdigest(),'purpose':'authentic PSoC4000T system declarations; BSP/producer identity not established','license':'Apache-2.0','modified':False},indent=2)+'\n')
print(hashlib.sha256(data).hexdigest())

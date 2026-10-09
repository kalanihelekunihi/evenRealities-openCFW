from pathlib import Path
import json,hashlib,urllib.request
O=Path(__file__).resolve().parent;pin='7923059bff6c120c6fb74b63c7553ea345c0a8f3';paths=['newlib/libc/machine/arm/memcpy-stub.c','include/arm-acle-compat.h','newlib/libc/string/memcpy.c','newlib/libc/string/local.h','newlib/libc/ctype/local.h','newlib/libc/locale/setlocale.h','COPYING.NEWLIB'];rows=[]
for name in paths:
 url='https://raw.githubusercontent.com/mirror/newlib-cygwin/'+pin+'/'+name
 data=urllib.request.urlopen(url,timeout=30).read();p=O/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);rows.append({'url':url,'upstream_path':name,'local':str(p.relative_to(O)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(O/'acquisition.json').write_text(json.dumps({'revision':pin,'pin_basis':'Official Arm14.2 release metadata read by discovery; mirror files at exact revision, no cryptographic signature claim','files':rows},indent=2)+'\n');print('acquired unchanged files',len(rows))

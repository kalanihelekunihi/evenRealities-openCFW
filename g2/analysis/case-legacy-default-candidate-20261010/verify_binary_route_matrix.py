#!/usr/bin/env python3
"""Native routing-only check for test binary_known_dispatch; no lower semantics."""
from pathlib import Path
import tempfile,subprocess,ctypes,json,hashlib
D=Path(__file__).resolve().parent;root=D.parents[2]
src=root/'g2/components/case/legacy_default_candidate_20261010/binary_known_dispatch.c'
names=['forward','3d','unknown','14','3e','3f','51','56','5e','5f','local_four']
ids={n:i+1 for i,n in enumerate(names)}
with tempfile.TemporaryDirectory() as td:
 p=Path(td);stub=p/'stubs.c';parts=['#include <stdint.h>']
 for n,i in ids.items():parts.append(f'uint32_t case_binary_{n}_candidate(const uint8_t *p,uint32_t n,uint32_t mode){{(void)p;(void)n;(void)mode;return {i};}}' if n in ['forward','3d'] else f'uint32_t case_binary_{n}_candidate(const uint8_t *p,uint32_t n){{(void)p;(void)n;return {i};}}')
 stub.write_text('\n'.join(parts)+'\n');lib=p/'route.so';subprocess.run(['cc','-shared','-fPIC',str(src),str(stub),'-o',str(lib)],check=True);f=ctypes.CDLL(str(lib)).case_binary_known_dispatch;f.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)];f.restype=ctypes.c_bool
 rows=[]
 for dest in range(256):
  for op in range(256):
   frame=(ctypes.c_uint8*32)();frame[0]=op;frame[2]=dest;result=ctypes.c_uint32(0);ok=f(frame,32,1,ctypes.byref(result))
   if dest!=2:expected=ids['3d'] if op==0x3d else ids['forward']
   elif op in [0x06,0x41]:expected=0
   elif op in [0x50,0x5c,0x5d,0x68]:expected=ids['local_four']
   else:expected=ids.get(f'{op:02x}',ids['unknown']) if op!=0x3d else ids['unknown']
   assert (ok,result.value if ok else 0)==(expected!=0,expected),(dest,op,ok,result.value,expected)
   rows.append([dest,op,expected])
out=dict(status='PASS_BINARY_ROUTING_ONLY',cases=len(rows),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),linked_arm_object_sha256=hashlib.sha256((D/'binary_known_linked.o').read_bytes()).hexdigest(),limits=['Native stub test checks dispatch choice only, not ARM lower ABI or stock behavior.','Two destination-2 special values explicitly unsupported by bounded dispatcher.','Not a public case_binary_command provider.'],counts={'supported':sum(x[2]!=0 for x in rows),'unsupported':sum(x[2]==0 for x in rows)})
(D/'binary-route-matrix.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['cases'],out['counts'])

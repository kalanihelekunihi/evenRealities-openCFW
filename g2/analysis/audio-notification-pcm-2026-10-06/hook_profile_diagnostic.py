#!/usr/bin/env python3
"""Same original notification with broad/scoped hooks; diagnostic, no coverage credit."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('v',ROOT/'g2/components/foundation/audio_pcm_consumer/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';raw=blob.read_bytes()[32:];results=[]
for broad in [False,True]:
 m=v.Machine([dict(address=v.cache.BASE,memory_size=len(raw),data=raw,flags=5)])
 if broad:m.cpu.hook_add(m.u.UC_HOOK_MEM_READ|m.u.UC_HOOK_MEM_WRITE,m.memory)
 history=[]
 def record(uc,pc,size,_):
  if 0x441f08<=pc<=0x441f12:history.append(dict(pc=hex(pc),r0=hex(uc.reg_read(m.a.UC_ARM_REG_R0)),bytes=bytes(uc.mem_read(pc,size)).hex()))
 m.cpu.hook_add(m.u.UC_HOOK_CODE,record);r=m.invoke('notify')
 expected=v.DATA+(24 if broad else 12)
 assert m.r(v.Q+4)==expected
 assert any(x['pc']=='0x441f0c' for x in history)==(not broad)
 assert m.r(v.Q+0x38)==1 and bytes(m.cpu.mem_read(v.DATA,12))==bytes.fromhex('020000000000000000000000')
 results.append(dict(profile='broad' if broad else 'scoped',pcWriteTo=hex(m.r(v.Q+4)),history=history,notification_disposition=r['cut'],queue_control=r['queue']))
result=dict(status='EXPECTED_PROFILE_DIVERGENCE',firmware_sha256=v.sha(blob),results=results,coverage_credit=False,conclusion='Adding broad memory observation skips unconditional caller LDR441f0c after original memcpy; scoped executes it. No original/C mutation or callee replacement; native engine internal cause unproven.')
p=Path(__file__).with_name('hook-profile-results.json');p.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

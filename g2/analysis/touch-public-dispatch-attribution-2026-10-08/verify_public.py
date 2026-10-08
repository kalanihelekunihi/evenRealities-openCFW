"""Original vs compiled pinned public dispatcher with synthetic callback probe."""
from pathlib import Path
import json,struct,sys,hashlib
D=Path(__file__).resolve().parent;s=D.parent/'touch-scan-isr-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('for start,count,enable,iir,irq')[0],ns);g=ns['g'];rows=[]
for base in [0,1,0xffffffff]:
 for context,internal in [(0x200004ec,0x20000c50),(0x20002000,0x20003500)]:
  vals=[]
  for native in [False,True]:
   u=g['guest']();u.mem_write(context+8,struct.pack('<I',internal));u.mem_write(internal+16,struct.pack('<I',g['symbols']['touch_dispatch_probe']));u.mem_write(0x20009200,struct.pack('<II',0,17));g['call'](u,g['symbols']['Cy_CapSense_InterruptHandler_V3Lp'] if native else 0x5fba,[base,context]);vals.append(bytes(u.mem_read(0x20000000,0x10000)));assert struct.unpack('<II',u.mem_read(0x20009200,8))==(context,18)
  assert vals[0]==vals[1];rows.append({'ignored_base':hex(base),'context':hex(context),'internal':hex(internal),'calls':1,'callback_argument':hex(context)})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Public dispatcher and original0x5fba execute directly, no function-entry stubs.','Callback is a compiled synthetic count/argument probe, not an actual project ISR or unknown vendor implementation.','Direct calls do not test physical IRQ delivery or null callback faults.']},indent=2)+'\n');print('PASS',len(rows))

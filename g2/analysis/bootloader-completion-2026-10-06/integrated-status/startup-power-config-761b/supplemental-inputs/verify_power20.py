"""Selector20 caller chain; native special/query/critical/status loops, clock API cuts."""
from pathlib import Path
import hashlib,json,itertools
base=Path(__file__).with_name('verify.py');code=base.read_text().split('fixtures=[]')[0]
code=code.replace('trace={}\nENTRIES=',"BEGIN=0x08000130;END=0x08000140\ntrace={}\nENTRIES=")
code=code.replace('def run(source,name,f):',"ENTRIES.update({'power-enter':('opencfw_bl_mspi_mode_enter',0x41bf84,0x41c17a),'power-leave':('opencfw_bl_mspi_mode_leave',0x41c17a,0x41c2d8)})\ndef run(source,name,f):")
code=code.replace("def record(cpu,access,p,size,value,user):writes.append([p,size,value&((1<<(8*size))-1)])", "def record(cpu,access,p,size,value,user):\n  writes.append([p,size,value&((1<<(8*size))-1)])\n  if p==0x40021004 and f.get('ack',True):w(0x40021008,(r(0x40021008)&~0x40000)|(value&0x40000))")
code=code.replace("if pc in [CFG,NOTIFY,SPECIAL]:", "for symbol,original,label in [('clock_request',0x4222f0,'request'),('clock_release',0x422364,'release'),('opencfw_bl_clock_release_all',0x4223d8,'release-all')]:\n   entry=(symbols[symbol]&~1) if source else original\n   if pc==entry:\n    events.append(['clock',label,u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)] if label!='release-all' else ['clock',label,u.reg_read(a.UC_ARM_REG_R0)])\n    u.reg_write(a.UC_ARM_REG_R0,7);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return\n  if pc in [CFG,NOTIFY,SPECIAL,BEGIN,END]:")
code=code.replace("elif pc==NOTIFY:events.append(['notify',irq])", "elif pc==NOTIFY:events.append(['notify',irq])\n   elif pc==BEGIN:events.append(['begin',irq])\n   elif pc==END:events.append(['end',irq])")
code=code.replace("w(0x40021008,0x40000 if f.get('busy',False) else 0)", "w(0x40021004,f.get('control',0));w(0x40021008,0x40000 if f.get('busy',False) else 0)")
code=code.replace("[(4,CFG),(0x24,SPECIAL),(0x28,NOTIFY)]", "[(4,CFG),(0x24,SPECIAL),(0x28,NOTIFY),(0xc,BEGIN),(0x10,END)]")
code=code.replace("0x40021090]]}","0x40021090,0x40021004,0x40021008]]}")
exec(compile(code,str(base),'exec'))
rows=[]
for name,control,busy,cached,saved,ack,callbacks,irq in itertools.product(['power-enter','power-leave'],[0,0x40000],[False,True],[0,3],[0,3],[False,True],[False,True],[0,1]):
 f=dict(mode=20,control=control,busy=busy,special_cached=cached,special_saved=saved,ack=ack,callbacks=callbacks,irq=irq)
 stock=run(False,name,f);source=run(True,name,f);assert stock==source,(name,f,stock,source);rows.append({'name':name,'fixture':f,'result':stock})
r={'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'base_runner_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(p):b for p,b in sorted(trace.items())},'limits':['Selector20 actual power enter/leave invokes native special-mode, query, critical and status polling. Clock request/release/release-all return7 equally, callback bodies/delay controlled.','Command writes cause synthetic status-bit acknowledgement in ack=true fixtures; no physical hardware timing, task scheduling or drain proof. Callback config payload compared only firstbyte, consistent with prior stock ABI evidence.']};args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows))

"""Native run/special-mode cluster; only elapsed-delay and registered callbacks controlled."""
import argparse,hashlib,json,itertools,struct,importlib.util
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5];sp=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(sp);sp.loader.exec_module(elf)
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-run-power-mode-candidate.elf'));ap.add_argument('--output',type=Path,default=Path(__file__).with_name('comparison.json'));args=ap.parse_args();_,segments,symbols=elf.elf_info(args.elf)
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
STOP=0x08000000;CFG=0x08000100;NOTIFY=0x08000110;SPECIAL=0x08000120;trace={}
ENTRIES={'mode':('opencfw_boot_control_mode_two',0x41ba80,0x41bae8),'transition':('opencfw_boot_control_transition',0x41b954,0x41ba80),'special':('opencfw_boot_power_special_mode',0x41bae8,0x41bbd0),'hook':('opencfw_boot_power_special_hook',0x41cde0,0x41cdfa)}
def run(source,name,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);mapped=set()
 for lo,size in [(0x410000,0x25000),(0x20000000,0x40000),(STOP,0x10000),(0x40004000,0x1000),(0x40020000,0x2000)]:u.mem_map(lo,size);mapped.update(range(lo,lo+size,4096))
 if source:
  for seg in segments:
   address,data=seg['address'],seg['data']
   for p in range(address&~4095,(address+seg['memory_size']+4095)&~4095,4096):
    if p not in mapped:u.mem_map(p,4096);mapped.add(p)
   u.mem_write(address,data)
 else:u.mem_write(0x410000,blob)
 def w(p,x):u.mem_write(p,struct.pack('<I',x&0xffffffff))
 def r(p):return int.from_bytes(u.mem_read(p,4),'little')
 events=[];writes=[];delays=0;done=False
 def record(cpu,access,p,size,value,user):writes.append([p,size,value&((1<<(8*size))-1)])
 def code(cpu,pc,size,user):
  nonlocal delays,done
  if pc==STOP:done=True;u.emu_stop();return
  if not source and 0x410000<=pc<0x435000:trace[pc]=bytes(u.mem_read(pc,size)).hex()
  delay=symbols['opencfw_boot_control_delay_us']&~1 if source else 0x41d1c0
  if pc==delay:
   delays+=1;events.append(['delay',u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_PRIMASK)])
   if delays==f.get('wake_after'):w(0x40004030,r(0x40004030)|0x01000000)
   if delays==f.get('ready_after'):
    reported=f.get('reported',f['mode']&3);w(0x40021000,(r(0x40021000)&~0x18)|((reported&3)<<3)|4)
   u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if pc in [CFG,NOTIFY,SPECIAL]:
   regs=[u.reg_read(x) for x in [a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2]];irq=u.reg_read(a.UC_ARM_REG_PRIMASK)
   if pc==CFG:events.append(['config',regs[0],regs[1],u.mem_read(regs[2],1)[0],irq])
   elif pc==NOTIFY:events.append(['notify',irq])
   else:events.append(['special',regs[0],regs[1],irq])
   u.reg_write(a.UC_ARM_REG_R0,f.get('callback_status',7));u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
 u.hook_add(UC_HOOK_CODE,code)
 for lo,hi in [(0x40004000,0x40004fff),(0x40020000,0x40021fff)]:u.hook_add(UC_HOOK_MEM_WRITE,record,begin=lo,end=hi)
 w(0x40021108,0xa5a50000|(f.get('gate',3)<<4));w(0x40021000,0xa5a50000|(f.get('reported',f['mode']&3)<<3)|(4 if f.get('ready',True) else 0))
 w(0x40004044,0x55550000|(0x20 if f.get('wake_enabled',False) else 0));w(0x40004030,0x54550000|(0x01000000 if f.get('wake',True) else 0));w(0x40021008,0x40000 if f.get('busy',False) else 0)
 w(0x4002108c,0xa5a5a5a5);w(0x40021090,0x5a5a5a5a);u.mem_write(0x20000552,bytes([f.get('cached',0)]));u.mem_write(0x200271a5,bytes([f.get('special_cached',1),f.get('special_saved',2)]))
 for offset,p in [(4,CFG),(0x24,SPECIAL),(0x28,NOTIFY)]:w(0x20026e38+offset,p|1 if f.get('callbacks',False) else 0)
 u.reg_write(a.UC_ARM_REG_XPSR,0x01000000);u.reg_write(a.UC_ARM_REG_SP,0x2002f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1);u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('irq',0));u.reg_write(a.UC_ARM_REG_R0,f['mode']);u.reg_write(a.UC_ARM_REG_R1,f.get('second',0x12345678));symbol,stock,_=ENTRIES[name];u.emu_start((symbols[symbol] if source else stock)|1,STOP+2,count=100000);assert done,(source,name,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
 return {'return':u.reg_read(a.UC_ARM_REG_R0),'events':events,'writes':writes,'irq':u.reg_read(a.UC_ARM_REG_PRIMASK),'cached':u.mem_read(0x20000552,1)[0],'special':bytes(u.mem_read(0x200271a5,2)).hex(),'registers':[r(p) for p in [0x40021000,0x40004044,0x40004030,0x4002108c,0x40021090]]}
fixtures=[]
for name,mode,gate,cached,callbacks,irq in itertools.product(['mode','transition'],[0,1,2,3,255,257,258],[0,3],[0,1,2],[False,True],[0,1]):fixtures.append((name,dict(mode=mode,gate=gate,cached=cached,callbacks=callbacks,irq=irq)))
for mode,gate,busy,cached,saved,callbacks,irq in itertools.product([0,1,2,3,255,256,259],[0,3],[False,True],[0,3],[0,3],[False,True],[0,1]):fixtures.append(('special',dict(mode=mode,gate=gate,busy=busy,special_cached=cached,special_saved=saved,callbacks=callbacks,irq=irq)))
for name,mode,ready_after,wake_after,enabled,callbacks in itertools.product(['mode','transition'],[1,2],[1,2,19,20,21,None],[1,2,16,17,None],[False,True],[False,True]):fixtures.append((name,dict(mode=mode,ready=False,wake=False,ready_after=ready_after,wake_after=wake_after,wake_enabled=enabled,callbacks=callbacks,cached=0)))
for mode,second,callbacks,status,irq in itertools.product([0,1,0x101,0xffffffff],[0,3,0x103,0xffffffff],[False,True],[0,7],[0,1]):fixtures.append(('hook',dict(mode=mode,second=second,callbacks=callbacks,callback_status=status,irq=irq)))
for mode in [1,2]:fixtures.append(('mode',dict(mode=mode,reported=0,cached=0,ready=True,callbacks=True)))
rows=[]
for name,f in fixtures:
 stock=run(False,name,f);source=run(True,name,f)
 if stock!=source:
  args.output.with_suffix('.failure.json').write_text(json.dumps({'name':name,'fixture':f,'stock':stock,'source':source},indent=2)+'\n');raise AssertionError((name,f,stock,source))
 rows.append({'name':name,'fixture':f,'result':stock})
for p,b in trace.items():assert bytes.fromhex(b)==blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]
used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
r={'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'visited_body_bytes':{name:len(used&set(range(lo,hi))) for name,(_,lo,hi) in ENTRIES.items()},'original_trace':{hex(p):b for p,b in sorted(trace.items())},'comparisons':rows,'limits':['Stock/source run-mode wrapper, transition, special-mode, query/descriptors, critical and wait-loop source execute natively. Only elapsed delay and registered callback bodies are controlled, with ordered MMIO writes/irq/cache state compared.','Synthetic ready/wake changes at chosen delay call, not hardware acknowledgement/timing/scheduling or physical power-mode validation. No SRAM write hook or copy answer models.','Main alias binding is distinct from existing source existence; this suite does not itself certify integration reachability.']};args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows),r['visited_body_bytes'])

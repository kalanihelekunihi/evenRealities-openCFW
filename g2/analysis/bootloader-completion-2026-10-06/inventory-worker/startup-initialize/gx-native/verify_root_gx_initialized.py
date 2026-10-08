"""Execute stock bytes and independent source leaves; callback bodies controlled."""
from pathlib import Path
import sys,json,hashlib,struct,itertools,importlib.util
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[6]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
_,segments,symbols=elf.elf_info(args.elf)
entries={'write':('opencfw_boot_startup_sleep_fields_write',0x41c9ca,0x41ca08),'read':('opencfw_boot_startup_sleep_fields_read',0x41ca0c,0x41ca2c)}
for name,lo,hi in [('20',0x41cdca,0x41cde0),('24',0x41cde0,0x41cdfa),('28',0x41cdfa,0x41ce10),('30',0x41ce10,0x41ce26),('34',0x41ce26,0x41ce3c),('38',0x41ce3c,0x41ce52)]:entries[name]=('opencfw_boot_startup_hook'+name,lo,hi)
entries['init']=('opencfw_boot_startup_initialize_abi',0x41c4b4,0x41c7de)
CHILDREN=[4334894, 4309370, 4309720, 4308868, 4307224, 4309792, 4330824, 4312658, 4307920, 4308534, 4307180]
stock_clock_cuts={0x41d1c0:'delay',0x41d246:'poll',0x41d3e4:'gpio',0x41d90e:'power_read',0x41d92c:'power_update',0x41ca5c:'prepare',0x41bf84:'mode_enter',0x41c17a:'mode_leave',0x41e348:'cache',0x41caa2:'finish'}
source_clock_names={'opencfw_hal_delay_us':'delay','opencfw_hal_status_poll':'poll','opencfw_legacy_gpio_mode':'gpio','opencfw_power_register_read':'power_read','opencfw_bl_power_register_update':'power_update','opencfw_low_power_prepare':'prepare','opencfw_bl_mspi_mode_enter':'mode_enter','opencfw_bl_mspi_mode_leave':'mode_leave','opencfw_cache_invalidate':'cache','opencfw_low_power_finish':'finish'}
source_clock_cuts={symbols[k]&~1:v for k,v in source_clock_names.items()}
scatter=json.loads((Path(__file__).parent/"scatter-selector-table.json").read_text())
trace={}
def run(source,name,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,sz in [(0,0x1000),(0x410000,0x25000),(0x08000000,0x20000),(0x10000,0x10000),(0x30000,0x10000),(0x20000000,0x40000),(0xe000e000,0x1000),(0xe001e000,0x1000),(0x40000000,0x300000),(0x47ff0000,0x10000)]:u.mem_map(lo,sz)
 if source:
  for seg in segments:u.mem_write(seg['address'],seg['data'])
 else:u.mem_write(0x410000,blob)
 def w(p,x):u.mem_write(p,struct.pack('<I',x&0xffffffff))
 w(0xe000ed14,f.get('scr',0));w(0xe001e300,f.get('value',0));u.mem_write(0x20001000,b'\xa5'*4)
 if name not in ['read','write','init']:w(0x20026e38+int(name,16),0x08000101 if f['present'] else 0)
 
 if name=='init':
  for p in [0x4000885c,0x40020250,0x4002021c,0x400201bc,0x40004044,0x40004120,0x40020448,0x4002036c,0x40020088,0x40020044,0x4002004c,0x40020374,0x40020080,0x400201b0,0x40020344,0x4002034c,0x40020358,0x40020354,0x4002037c,0x40020380,0x400211c8]:w(p,f.get('seed',0))
  
  for start,key in [(0x200000a4,'vddc_rank'),(0x200000f4,'vddf_rank')]:
   for i,v in enumerate(scatter[key]):w(start+4*i,v)
  w(0x20000148,20)
  w(0x400201bc,f.get('gate29',0));w(0x40021108,f.get('gate',0)<<4);w(0x4002000c,f['revision']);w(0x20000098,f['variant']);w(0x200267f8,0x1f01600d if f.get('cached',True) else 0)
  for p in range(0x2002704c,0x2002708c,4):w(p,0xa5a5a5a5)
  for p in [0x200271a3,0x200271a8,0x2000009c,0x200271a5]:u.mem_write(p,bytes([f.get('saved',0) if p==0x200271a8 else (f.get('skipdebug',0) if p==0x200271a3 else (f.get('modebyte',0) if p==0x200271a5 else 0))]))
  for slot in [0x20026e58,0x20026e5c,0x20026e68]:w(slot,0x08000101 if f.get('present',False) else 0)
 w(0x40021008,f.get('active',0)<<27);w(0x40008858,(0x5af0<<16)|f['clock_flags']);w(0x4000885c,f['clock_guard'])
 w(0x4001003c,0xdeadbeef);w(0x40004030,0x01000000)
 events=[];writes=[];done=False;in_clock=False;info_calls=0
 def hook(cpu,p,size,_):
  nonlocal done,in_clock,info_calls
  if p==0x08000000:done=True;u.emu_stop();return
  if p==0x40:
   events.append(['ROM40-wait',u.reg_read(a.UC_ARM_REG_R0)]);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if p==((symbols['opencfw_boot_device_mode_wait']&~1) if source else 0x421548):
   if f.get('rearm_otp_on_first_info') and info_calls==0:w(0x40021008,struct.unpack('<I',u.mem_read(0x40021008,4))[0]|0x08000000)
   info_calls+=1
  if p==0x48:
   address=u.reg_read(a.UC_ARM_REG_R0);dest=u.reg_read(a.UC_ARM_REG_R1);count=u.reg_read(a.UC_ARM_REG_R2);events.append(['ROM48-read',address,count])
   for i in range(count):w(dest+4*i,0x87654321)
   if f.get('drop_otp_ready') and address==0x42006840:w(0x40021008,struct.unpack('<I',u.mem_read(0x40021008,4))[0]&~0x08000000)
   u.reg_write(a.UC_ARM_REG_R0,f.get('failure',0));u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if source and p in [0x42a878,0x42ba00,0x42ac54,0x42bf54,0x42ab7c,0x42a036,0x42a04a,0x42bd8c,0x42bda0,0x42bdbc,0x42ae9c,0x42d848,0x42d692,0x42d6a6,0x42f3da,0x42f400,0x42d5f8,0x42d61e,0x42f38e]:
   raise RuntimeError(('unbound source callback',hex(p),f,[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]))
  if not source and 0x410000<=p<0x435000:trace[p]=bytes(u.mem_read(p,size)).hex()
  if p==((symbols['am_hal_pwrctrl_low_power_init_clockmux_fragment']&~1) if source else 0x41acb2):in_clock=True
  cuts=source_clock_cuts if source else stock_clock_cuts
  if in_clock and p in cuts:
   kind=cuts[p];regs=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
   fifth=struct.unpack('<I',u.mem_read(u.reg_read(a.UC_ARM_REG_SP),4))[0]
   if kind=='delay':event=[kind,regs[0]]
   elif kind=='poll':event=[kind,*regs,fifth]
   elif kind=='gpio':event=[kind,regs[0],u.mem_read(regs[1],1)[0] if regs[1] else None]
   elif kind in ['power_read','mode_enter','mode_leave']:event=[kind,regs[0]]
   elif kind in ['power_update','cache']:event=[kind,regs[0],regs[1]]
   else:event=[kind]
   events.append(event)
  if name=='init':
   for index,original in enumerate(CHILDREN):
    if original in CHILDREN or (in_clock and original in [0x41c17a,0x41bf84]):continue
    entry=0x08000200+index*0x10 if source else original
    if p==entry or (source and original==0x421548 and p==(symbols['opencfw_boot_device_mode_wait']&~1)):
     r0=u.reg_read(a.UC_ARM_REG_R0);r1=u.reg_read(a.UC_ARM_REG_R1);r2=u.reg_read(a.UC_ARM_REG_R2);r3=u.reg_read(a.UC_ARM_REG_R3);irq=u.reg_read(a.UC_ARM_REG_PRIMASK)
     event=[hex(original),irq]
     if original in [0x41c17a,0x41bf84]:event+=[r0]
     if original==0x41be36:event+=[r0]
     if original==0x41bbd0:event+=[r0,bytes(u.mem_read(r0,1)).hex()]
     if original==0x421548:event+=[r0,r1,r2,"stack" if r3>=0x20030000 else r3]
     result=0
     if original==0x41c2d8:event+=[r0];u.mem_write(r1,bytes([f.get('active',0)]))
     if original==0x41b918:w(r0,0x12345678)
     if original==0x421548:
      result=f.get('failure',0) if r1==f.get('fail_selector',0) else 0
      if not result:
       for i in range(r2):w(r3+4*i,0x87654321)
     if original==0x41b8ec:result=irq;u.reg_write(a.UC_ARM_REG_PRIMASK,1)
     events.append(event);u.reg_write(a.UC_ARM_REG_R0,result);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if p==0x08000100:raise AssertionError(('unexpected synthetic callback reached',source,f))
 def write(cpu,access,p,size,value,_):
  writes.append([p,size,value&((1<<(8*size))-1)])
  mapping={0x40021004:(0x40021008,[(0x00200000,0x00200000),(0x01000000,0x01000000),(0x02000000,0x02000000),(0x04000000,0x04000000)]+([(0x08000000,0x08000000)] if f.get("ack_power29",True) else [])),0x4002100c:(0x40021010,[(4,4),(0x40,0xc0),(0x80,0xc0),(0x400,0x400)])}
  if p==0x40021014:w(0x40021018,(value&15)|((value&16)<<2)|((value&32)<<2))
  if p==0x40021024:w(0x40021028,value&7)
  if p in mapping:
   status,masks=mapping[p];mask=0;ack=0
   for command,field in masks:
    mask|=field
    if value&command:ack|=field
   prior=struct.unpack('<I',cpu.mem_read(status,4))[0];w(status,(prior&~mask)|ack)
 u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x402fffff);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe000e000,end=0xe001efff)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_R0,0x20001000 if name=='read' else f.get('arg',0));u.reg_write(a.UC_ARM_REG_R1,f.get('second',0));u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('irq',0))
 u.reg_write(a.UC_ARM_REG_R5,f['ambient_r5']);u.reg_write(a.UC_ARM_REG_R7,f['ambient_r7'])
 u.reg_write(a.UC_ARM_REG_R1,0x10203040);u.reg_write(a.UC_ARM_REG_R2,0x55667788);u.reg_write(a.UC_ARM_REG_R3,0x89abcdef)
 for reg in [4,6,8,9,10,11]:u.reg_write(getattr(a,f'UC_ARM_REG_R{reg}'),0xa0000000+reg)
 pc=(symbols[entries[name][0]]&~1) if source else entries[name][1];u.emu_start(pc|1,0,count=500000);assert done
 if name=='init':return dict(registers=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)],callee_saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],stack=u.reg_read(a.UC_ARM_REG_SP),ret=u.reg_read(a.UC_ARM_REG_R0),writes=writes,events=events,irq=u.reg_read(a.UC_ARM_REG_PRIMASK),info_cache=bytes(u.mem_read(0x200267f8,128)).hex(),calibration=bytes(u.mem_read(0x2002704c,64)).hex(),saved=bytes(u.mem_read(0x200271a8,1)).hex(),revisionflag=bytes(u.mem_read(0x2000009c,1)).hex())
 return dict(ret=None if name=='read' else u.reg_read(a.UC_ARM_REG_R0),writes=writes,events=events,output=bytes(u.mem_read(0x20001000,4)).hex(),irq=u.reg_read(a.UC_ARM_REG_PRIMASK))
fixtures=[]
for revision,saved,flags,r5,r7,guard in itertools.product([32,33,34,35,36],[0,1],[0,2,0x45,0x7f,0x20,0x0c,0x10],[0x20027064,0xa5b6c7d8],[0,0x11223344],[0,2]):
 fixtures.append(dict(revision=revision,variant=1,gate=3,seed=0xffffffff,saved=saved,present=True,irq=0,clock_flags=flags,ambient_r5=r5,ambient_r7=r7,clock_guard=guard))
legacy_fixtures=[]
for revision,variant,gate,seed,saved,present,irq in itertools.product([32,33,34,35,36],[0,1,2,3,4],[0,3],[0,0xffffffff],[0,1],[False,True],[0,1]):legacy_fixtures.append(dict(revision=revision,variant=variant,gate=gate,seed=seed,saved=saved,present=present,irq=irq))
for selector,status,active,skipdebug in itertools.product([0x210,0x245],[0,7],[0,1],[0,1]):legacy_fixtures.append(dict(revision=34,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=0,cached=False,fail_selector=selector,failure=status,gate29=8,active=active,skipdebug=skipdebug,modebyte=255))
for f in legacy_fixtures:
 f.update(clock_flags=0x7f,ambient_r5=0xa5b6c7d8,ambient_r7=0x11223344,clock_guard=0);fixtures.append(f)
unbound=[];supported=[]
for f in fixtures:
 rev=f['revision'];var=f['variant'];opaque=(rev==35 and var>=2) or rev>=36
 if opaque:unbound.append(f)
 else:supported.append(f)
fixtures=supported
for revision in [32,33,34]:
 for skipdebug in [0,1]:
  fixtures.append(dict(revision=revision,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=1,cached=False,gate29=8,active=0,skipdebug=skipdebug,clock_flags=0x10,ambient_r5=0xa5b6c7d8,ambient_r7=0x11223344,clock_guard=0,ack_power29=False))
for revision in [32,33,34]:
 for skipdebug in [0,1]:
  fixtures.append(dict(revision=revision,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=1,cached=False,gate29=8,active=1,skipdebug=skipdebug,clock_flags=0x10,ambient_r5=0xa5b6c7d8,ambient_r7=0x11223344,clock_guard=0,drop_otp_ready=True))
for revision in [32,33,34]:
 for skipdebug in [0,1]:
  fixtures.append(dict(revision=revision,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=1,cached=False,gate29=0,active=0,skipdebug=skipdebug,clock_flags=0x10,ambient_r5=0xa5b6c7d8,ambient_r7=0x11223344,clock_guard=0))
  fixtures.append(dict(revision=revision,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=1,cached=False,gate29=8,active=0,skipdebug=skipdebug,clock_flags=0x10,ambient_r5=0xa5b6c7d8,ambient_r7=0x11223344,clock_guard=0,ack_power29=False,rearm_otp_on_first_info=True,drop_otp_ready=True))
rows=[]
for f in fixtures:
 stock=run(False,'init',f);source=run(True,'init',f)
 if stock!=source:args.output.with_suffix('.failure.json').write_text(json.dumps(dict(fixture=f,stock=stock,source=source),indent=2));raise AssertionError((f,stock,source))
 rows.append(dict(fixture=f,result=stock))
for p,b in trace.items():assert blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]==bytes.fromhex(b)
used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
r=dict(excluded_unbound_family_cases=len(unbound),excluded_family_limits="EM family installed-callback bodies are not yet bound in this image; only EM family cases are excluded because shared-memory configuration can invoke installed callback selector6 even when clock switching is skipped. No callback return stub substitutes for these families.",status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(blob).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_trace={hex(p):b for p,b in sorted(trace.items())},visited_body_bytes={name:len(used&set(range(lo,hi))) for name,(_,lo,hi) in entries.items()},comparisons=rows,limits=['Root orchestration and clock body execute original instructions versus compiled source together; no root children and clock children execute native source/original bodies with synthetic acknowledgement and ROM40 timing. Sleep fields, hooks and installed source-defined callbacks native; no generic callback return stub is permitted.','No root or clock child body cut remains. Only absent resident ROM40/48 and synthetic peripheral acknowledgement/readiness transitions are controlled; hardware, live IRQ scheduling and drain unverified.','Source root ABI wrapper captures ambient R5/R7 and reproduces mutated saved R1/R2/R3; R0-R3,R4-R11,SP,PRIMASK compared. No root child body is controlled; clock children native with synthesized acknowledgement and resident ROM40 timing. SPOT dispatcher/four initial callbacks/timer/installed autosw hook, power29 query, critical-save/disable and trim-version copy execute native source/original bodies. TON state/trim callbacks and native gate/delay providers plus INFO selector/dispatcher/ROM thunk and debug release execute original/source bodies; only absent resident ROM40/48 bodies are controlled; trim cache is seeded0..4, so its uncached ROM path is not exercised here. Standalone candidate, not promoted or counted as native root closure.'])
args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows),r['visited_body_bytes'])

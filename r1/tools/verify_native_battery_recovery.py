#!/usr/bin/env python3
"""Recover native timeout/state/log semantics and saved-register return words."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-recovery';D=0x20016b84;B=0x20006890;T=0x20002000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'osKernelGetTickCount':0x7d28c,'osKernelGetTickFreq':0x7d2a4,'r1_battery_charging_progress_reset':0x4fe5c,'r1_battery_charging_initial_curve':0x4ff3c,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_4':0x799f8}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_recovery.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 for suffix in ('body','pseudocode'):
  p=OUT/f'rea-3db70-{suffix}.json';p.write_bytes((BASE/'native-battery-runtime'/f'rea-next-3db70-{suffix}.json').read_bytes());evidence[p.name]=sha(p)
 q=json.loads((OUT/'rea-3db70-body.json').read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==272
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x3db70&length=412']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x3db70-0x27000:0x3db70-0x27000+412];p=OUT/'ghidra-body-data.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 modes=[(i,) for i in range(8)]+[(0,4,2),(1,2),(4,0,7,0),(0,0,0,1,7),(0xffffffff,0)]
 times=[(0,0,0),(119999,0,1000),(120000,0,1000),(120001,0,1000),(0,0xffffffff,1),(0xffffffff,0,1),(0xffffffff,0,0xffffffff),(0xffffffff,0,35791394),(0xffffffff,0,35791395)]
 cases=[]
 def fixture(**changes):
  f=dict(state=1,level=50,previous=50,done=0,reference=4000,voltage=4035,now=120000,last=0,frequency=1000,curve=60,stamp=0,sequence=(0,),mutation=False,seeds=(0x12345678,0x89abcdef));f.update(changes);return f
 for state,level,previous,done,voltages,time in itertools.product((0,1,2,0xffffffff),(0,1,50,98,99,255),(0,50,98,255),(0,1),((2399,4035),(2400,2400),(4000,4034),(4000,4035),(4000,65535),(65535,65535)),times):
  cases.append(fixture(state=state,level=level,previous=previous,done=done,reference=voltages[0],voltage=voltages[1],now=time[0],last=time[1],frequency=time[2]))
 for sequence,curve,stamp,mutation,seeds in itertools.product(modes,(0,49,50,60,100,101,0xffffffff),(0,1,0xffffffff),(False,True),((0,0),(0x12345678,0x89abcdef))):cases.append(fixture(sequence=sequence,curve=curve,stamp=stamp,mutation=mutation,seeds=seeds))
 machines=[];states={};counts={n:0 for n in P};sections={}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .ring 0x3dc88 : { *(.r1.battery_recovery.ring) } .sdk 0x3dcd0 : { *(.r1.battery_recovery.sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_battery_device_context='+hex(D),'--defsym=r1_battery_runtime_context='+hex(B),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  for name,address in [('ring',0x3dc88),('sdk',0x3dcd0)]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[address-0x27000:address-0x27000+p.stat().st_size];sections[name]={'address':address,'bytes':p.stat().st_size,'sha256':sha(p)}
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   if a not in kinds:
    if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   f=states[id(u)];n=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];event=(n,);value=0
   if n=='osKernelGetTickCount':value=f['now']
   elif n=='osKernelGetTickFreq':value=f['frequency']
   elif n=='r1_battery_charging_progress_reset':
    if f['mutation']:u.mem_write(D+42,struct.pack('<H',4050));u.mem_write(B+10,struct.pack('<H',3900))
   elif n=='r1_battery_charging_initial_curve':
    assert args[0]==struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0];event+=(args[0],);value=f['curve']
    if f['mutation']:u.mem_write(D+44,b'\x46');u.mem_write(B+10,struct.pack('<H',3850))
    f['log_reference']=struct.unpack('<H',bytes(u.mem_read(B+10,2)))[0]
   elif n=='r1_structured_log_mode_get':
    value=f['sequence'][f['mode_index']%len(f['sequence'])];f['mode_index']+=1;event+=(value,)
    if f['mutation']:
     u.mem_write(D+44,bytes([(bytes(u.mem_read(D+44,1))[0]+1)&255]));u.mem_write(D+42,struct.pack('<H',struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0]+2));u.mem_write(T,struct.pack('<I',(struct.unpack('<I',bytes(u.mem_read(T,4)))[0]+3)&0xffffffff))
   elif n=='r1_structured_log_format':
    stack=struct.unpack('<3I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),12)));assert args[:3]==[0x09000000,0x3dc88,0x3dc88];assert stack==(f['log_reference'],struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0],struct.unpack('<I',bytes(u.mem_read(T,4)))[0]);event+=tuple(args)+stack;f['saved']=list(stack)
    if f['mutation']:u.mem_write(D+42,struct.pack('<H',4100));u.mem_write(T,struct.pack('<I',7));u.mem_write(D+44,b'\x50')
   else:
    stack=struct.unpack('<2I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),8)));assert args[0:2]==[0x001c0002,0x3dcd0] and args[3]==f['log_reference'];assert stack==(struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0],struct.unpack('<I',bytes(u.mem_read(T,4)))[0]);event+=tuple(args)+stack;f['saved'][:2]=stack
   f['trace'].append((event,bytes(u.mem_read(D,68)),bytes(u.mem_read(B,44)),bytes(u.mem_read(T,4))))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for index,f in enumerate(cases):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={**f,'trace':[],'mode_index':0,'saved':[T,*f['seeds']]};u.mem_write(D-4,b'\xa5'*76);u.mem_write(B-4,b'\x96'*52);u.mem_write(D+44,bytes([f['level']]));u.mem_write(D+42,struct.pack('<H',f['voltage']));u.mem_write(B+3,bytes([f['previous'],f['done']]));u.mem_write(B+10,struct.pack('<H',f['reference']));u.mem_write(B+32,struct.pack('<I',f['last']));u.mem_write(T,struct.pack('<I',f['stamp']))
    for reg,value in [(UC_ARM_REG_R0,f['state']),(UC_ARM_REG_R1,T),(UC_ARM_REG_R2,f['seeds'][0]),(UC_ARM_REG_R3,f['seeds'][1]),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_battery_stuck_charge_recovery'] if candidate else 0x3db70)|1,0x20000100,count=5000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert regs==states[id(u)]['saved'],(index,candidate,regs,states[id(u)]['saved'])
    results.append((bytes(u.mem_read(D-4,76)),bytes(u.mem_read(B-4,52)),bytes(u.mem_read(T,4)),states[id(u)]['trace'],regs))
   assert results[0]==results[1],(index,f,[(i,x,y) for i,(x,y) in enumerate(zip(*results)) if x!=y])
   for event in results[0][3]:counts[event[0][0]]+=1
 vp.write_text(json.dumps(dict(comparisons=len(cases),provider_calls_per_side=counts,mode_sequences=len(modes),full_r1_r2_r3_checked=True,source_descriptor_sections=sections,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Tick/reset/initial-curve/log providers are fixtures; actual updater and provider composition remains open','Native saved argument words and logger overwrites preserved for selected compiler; other compilers/LTO require revalidation','Runtime state/handle initialization, physical atomicity/timing/concurrency and original image identity remain gates']),indent=2)+'\n');print('Battery recovery:',len(cases),counts)
if __name__=='__main__':main()

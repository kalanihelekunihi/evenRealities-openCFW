#!/usr/bin/env python3
"""Compare counter cadence, repeated logger modes and six-argument log forwarding."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-diagnostic';D=0x20016b84;T=0x20002000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_structured_log_mode_get':0x914ec,'r1_batcfg_byte0_get':0x7bb44,'r1_batcfg_word1_signed_get':0x7bb7c,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8,'nrf_log_frontend_std_4':0x799f8}
SECTIONS={'period_ring':(0x3dad0,49),'period_sdk':(0x3db04,43),'offset_ring':(0x3db30,30),'offset_sdk':(0x3db50,24),'charge_ring':(0xc00bc,73),'charge_sdk':(0xc0108,67)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_diagnostic.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 p=OUT/'rea-3d9b8.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-3d9b8-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==268;evidence[p.name]=sha(p)
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for name,a,z in [('body',0x3d9b8,440),('charge_ring',0xc00bc,73),('charge_sdk',0xc0108,67)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/f'ghidra-{name}.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 modes=[(i,) for i in range(8)]+[(0,4,2),(1,2),(4,0,7,0),(0,0,0,1,7),(0xffffffff,0)];machines=[];states={};counts={n:0 for n in P};sections={};comparisons=0
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { '+''.join(f'.{n} 0x{a:x} : {{ *(.r1.battery_diagnostic.{n}) }} ' for n,(a,z) in SECTIONS.items())+' .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_battery_device_context='+hex(D),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  for n,(a,z) in SECTIONS.items():
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[a-0x27000:a-0x27000+z];sections[n]={'address':a,'bytes':z,'sha256':sha(p)}
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()});formats={a:n for n,(a,z) in SECTIONS.items()}
  def hook(u,a,size,_):
   if a not in kinds:
    if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   f=states[id(u)];n=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];event=(n,);value=0
   if n=='r1_structured_log_mode_get':value=f['sequence'][f['mode_index']%len(f['sequence'])];f['mode_index']+=1;event+=(value,)
   elif n=='r1_batcfg_byte0_get':value=0xffffff03
   elif n=='r1_batcfg_word1_signed_get':value=0xfffffed4
   else:
    form=formats[args[1]];event+=(form,)
    if form.endswith('_ring'):
     assert n=='r1_structured_log_format' and args[2]==args[1];expected_header=0x0c400000 if form=='offset_ring' else 0x0d000000;assert args[0]==expected_header
     vals=[args[3]]+([] if form=='offset_ring' else list(struct.unpack('<3I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),12)))))
    else:
     assert args[0]==0x001c0003 and n==('nrf_log_frontend_std_1' if form=='offset_sdk' else 'nrf_log_frontend_std_4');vals=[args[2]] if form=='offset_sdk' else args[2:]+list(struct.unpack('<2I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),8))))
    if form.startswith('charge'):assert vals==list(f['payload'][:4])
    if form.startswith('offset'):assert vals==[0xfffffed4]
    if form.startswith('period'):
     assert vals[:2]==[bytes(u.mem_read(D+44,1))[0],struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0]] and vals[2:]==[f['payload'][4],0xffffff03]
    event+=tuple(vals)
   if f['mutation']:
    current=bytes(u.mem_read(f['counter'],1))[0];u.mem_write(f['counter'],bytes([(current+7)&255]));u.mem_write(D+42,struct.pack('<H',(struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0]+3)&65535))
   f['trace'].append((event,bytes(u.mem_read(D-4,76)),bytes(u.mem_read(T,4))))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for initial,sequence,payload,mutation,counter in itertools.product(range(256),modes,((0,0,0,0,0),(0x12345678,0x8000,0xffffffff,0xabcdef01,2),(0xffffffff,0xffff0000,0x80000000,0x1234,0xffffffff)),(False,True),(T,D+44)):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'sequence':sequence,'mode_index':0,'payload':payload,'counter':counter,'mutation':mutation};u.mem_write(D-4,b'\xa5'*76);u.mem_write(D+42,struct.pack('<H',3800));u.mem_write(D+44,b'\x32');u.mem_write(T,bytes(4));u.mem_write(counter,bytes([initial]));u.mem_write(0x2003f000,struct.pack('<II',*payload[3:]))
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR),(counter,*payload[:3],0x2003f000,0x20000101)):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_battery_diagnostic_cadence_step'] if candidate else 0x3d9b8)|1,0x20000100,count=5000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((bytes(u.mem_read(D-4,76)),bytes(u.mem_read(T,4)),states[id(u)]['trace']))
   assert results[0]==results[1],(initial,sequence,payload,mutation,counter,results);comparisons+=1
   for event in results[0][2]:counts[event[0][0]]+=1
 vp.write_text(json.dumps(dict(comparisons=comparisons,all_counter_bytes=True,mode_sequences=len(modes),provider_calls_per_side=counts,counter_aliases=[T,D+44],source_descriptor_sections=sections,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Mode/config/log providers are fixtures; actual updater/logger composition remains open','Callback mutation and a counter aliasing device level are compared; physical interrupts/concurrency unproven','Runtime state/handle initialization, canonical admission, full startup and original image identity remain gates']),indent=2)+'\n');print('Battery diagnostic:',comparisons,counts)
if __name__=='__main__':main()

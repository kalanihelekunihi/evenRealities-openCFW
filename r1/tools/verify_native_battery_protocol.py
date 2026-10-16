#!/usr/bin/env python3
"""Battery packet/log/raw-return contract and saved argument words."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-protocol';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_2':0x799d6,'r1_phone_cmd_send_op1':0x83896}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_protocol.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 p=OUT/'rea-8345c.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-8345c-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==108;evidence[p.name]=sha(p)
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for name,a,z in [('body',0x8345c,180),('ring',0xc0234,66)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/f'ghidra-{name}.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 modes=[(i,) for i in range(8)]+[(0,4,2),(1,2),(4,0,7,0),(0,0,0,1,7),(0xffffffff,0)];machines=[];states={};counts={n:0 for n in P};comparisons=0;sections={}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .ring 0xc0234 : { *(.r1.battery_protocol.ring) } .sdk 0x834d4 : { *(.r1.battery_protocol.sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  for name,a,z in [('ring',0xc0234,66),('sdk',0x834d4,60)]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[a-0x27000:a-0x27000+z];sections[name]={'address':a,'bytes':z,'sha256':sha(p)}
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   if a not in kinds:
    if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   f=states[id(u)];n=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];event=(n,);value=0
   if n=='r1_structured_log_mode_get':value=f['sequence'][f['mode_index']%len(f['sequence'])];f['mode_index']+=1;event+=(value,)
   elif n=='r1_structured_log_format':
    charge=struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0];assert args==[0x0c800000,0xc0234,0xc0234,f['level']] and charge==f['charge'];f['saved1']=charge;event+=tuple(args)+(charge,)
   elif n=='nrf_log_frontend_std_2':assert args==[0x001c0003,0x834d4,f['level'],f['charge']];event+=tuple(args)
   else:
    assert args[1:3]==[1,0] and bytes(u.mem_read(args[0],8))==f['packet'];event+=(f['packet'],1,0);value=f['raw']
    if f['mutation']:f['packet']=bytes((i*31+7)&255 for i in range(8));u.mem_write(args[0],f['packet'])
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for level,state,sequence,raw,mutation in itertools.product((*range(256),256,0xffffffff),(0,1,2,256,0x80000000,0xffffffff),modes,(0,1,0x80000000,0xffffffff),(False,True)):
   results=[];charge=1 if state else 2
   for candidate,u in enumerate(machines):
    states[id(u)]={'level':level,'charge':charge,'sequence':sequence,'mode_index':0,'packet':struct.pack('<II',(level&255)|(charge<<8),0),'saved1':state,'raw':raw,'mutation':mutation,'trace':[]};u.reg_write(UC_ARM_REG_R0,level);u.reg_write(UC_ARM_REG_R1,state);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_proto_report_battery_status'] if candidate else 0x8345c)|1,0x20000100,count=1500)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    f=states[id(u)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert u.reg_read(UC_ARM_REG_R0)==raw and regs==[f['saved1'],*struct.unpack('<II',f['packet'])];results.append((f['trace'],regs))
   assert results[0]==results[1];comparisons+=1
   for event in results[0][0]:counts[event[0]]+=1
 vp.write_text(json.dumps(dict(comparisons=comparisons,all_percentage_bytes=True,full_word_percentage_logs=True,mode_sequences=len(modes),full_r1_r2_r3_checked=True,raw_return_checked=True,provider_calls_per_side=counts,source_descriptor_sections=sections,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Mode/logger/operation1 endpoints are fixtures; actual lower protocol/updater composition remains open','Eight-byte packet, zero padding, nonzero state mapping and raw return/register words verified for selected compiler; other compiler/LTO settings need revalidation','Runtime/init, transport delivery, enabled full-graph logging and original image identity remain gates']),indent=2)+'\n');print('Battery protocol:',comparisons,counts)
if __name__=='__main__':main()

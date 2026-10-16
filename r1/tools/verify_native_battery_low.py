#!/usr/bin/env python3
"""Replay escalation thresholds, partial record ABI, tail event and callback mutation."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-low';D=0x20016b84;H=0x20006548;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_2':0x799d6,'r1_battery_voltage_get':0x91290,'time_backend_timestamp_thunk':0x8ada4,'r1_kv_dev_info_fields_set':0x73710,'osThreadFlagsSet':0x7d6f4,'r1_event_publish':0x8d8fc}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_low.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 p=OUT/'rea-3d88c.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-3d88c-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==176;evidence[p.name]=sha(p)
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x3d88c&length=300']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x3d88c-0x27000:0x3d88c-0x27000+300];p=OUT/'ghidra-body-data.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 modes=[(i,) for i in range(8)]+[(0,4,2),(1,2),(4,0,7,0),(0,0,0,1,7),(0xffffffff,0)];machines=[];states={};counts={n:0 for n in P};sections={};comparisons=0;outcomes={'reset':0,'ordinary':0,'event':0,'record':0}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .ring 0x3d940 : { *(.r1.battery_low.ring) } .sdk 0x3d980 : { *(.r1.battery_low.sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_battery_device_context='+hex(D),'--defsym=r1_low_battery_thread_handle='+hex(H),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  for name,a,z in [('ring',0x3d940,55),('sdk',0x3d980,49)]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[a-0x27000:a-0x27000+z];sections[name]={'address':a,'bytes':z,'sha256':sha(p)}
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   if a not in kinds:
    if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   f=states[id(u)];n=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];event=(n,);value=0
   if n=='r1_structured_log_mode_get':value=f['sequence'][f['mode_index']%len(f['sequence'])];f['mode_index']+=1;event+=(value,)
   elif n=='r1_structured_log_format':
    count=struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0];assert args==[0x08800000,0x3d940,0x3d940,struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0]] and count==bytes(u.mem_read(D+47,1))[0];event+=tuple(args)+(count,);f['saved'][0]=count
   elif n=='nrf_log_frontend_std_2':assert args==[0x001c0002,0x3d980,struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0],bytes(u.mem_read(D+47,1))[0]];event+=tuple(args)
   elif n=='r1_battery_voltage_get':value=f['voltage_word'];f['saved'][1]=(f['saved'][1]&0xffff0000)|((value&0x3fff)<<2)
   elif n=='time_backend_timestamp_thunk':value=f['timestamp'];f['saved'][0]=value
   elif n=='r1_kv_dev_info_fields_set':
    words=list(struct.unpack('<2I',bytes(u.mem_read(args[0],8))));assert words==f['saved'];event+=tuple(words);f['outcome']='record'
    if f['mutation']:
     words=[words[0]^0x12345678,words[1]^0x89abcdef];u.mem_write(args[0],struct.pack('<2I',*words));f['saved']=words;u.mem_write(H,struct.pack('<I',0x2000bbcc))
   elif n=='osThreadFlagsSet':assert args[:2]==[struct.unpack('<I',bytes(u.mem_read(H,4)))[0],1];event+=tuple(args[:2]);value=0x80000004
   else:assert args[:3]==[0x100c,0,0];event+=tuple(args[:3]);f['outcome']='event';f['saved']=[0x76543210,0xdeadbeef];value=0x80000007
   if f['mutation'] and n in ('r1_structured_log_mode_get','r1_structured_log_format','nrf_log_frontend_std_2'):
    current=bytes(u.mem_read(D+47,1))[0];u.mem_write(D+47,bytes([(current+3)&255]));u.mem_write(D+42,struct.pack('<H',(struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0]+7)&65535))
   f['trace'].append((event,bytes(u.mem_read(D-4,76)),bytes(u.mem_read(H,4))))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for voltage,initial,sequence,seeds,mutation in itertools.product((0,3349,3350,65535),range(256),modes,((0,0xffffffff),(0x123456a5,0x89abcdef)),(False,True)):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'sequence':sequence,'mode_index':0,'mutation':mutation,'saved':list(seeds),'voltage_word':0xffffffff if seeds[0]==0 else 0x12345678,'timestamp':seeds[0]^0xabcdef01,'outcome':'reset' if voltage>=3350 else 'ordinary'};u.mem_write(D-4,b'\xa5'*76);u.mem_write(D+42,struct.pack('<H',voltage));u.mem_write(D+47,bytes([initial]));u.mem_write(H,struct.pack('<I',0x2000aabb))
    for reg,value in [(UC_ARM_REG_R2,seeds[0]),(UC_ARM_REG_R3,seeds[1]),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_battery_low_escalation'] if candidate else 0x3d88c)|1,0x20000100,count=3000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    actual=[u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3)];assert actual==states[id(u)]['saved'],(voltage,initial,sequence,seeds,mutation,candidate,actual,states[id(u)]['saved'])
    if states[id(u)]['outcome']=='event':assert u.reg_read(UC_ARM_REG_R0)==0x80000007
    results.append((bytes(u.mem_read(D-4,76)),bytes(u.mem_read(H,4)),states[id(u)]['trace'],actual,states[id(u)]['outcome']))
   assert results[0]==results[1];comparisons+=1;outcomes[results[0][-1]]+=1
   for event in results[0][2]:counts[event[0][0]]+=1
 vp.write_text(json.dumps(dict(comparisons=comparisons,all_counter_bytes=True,mode_sequences=len(modes),provider_calls_per_side=counts,outcomes=outcomes,full_r2_r3_checked=True,event_tail_raw_return_checked=True,source_descriptor_sections=sections,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Log/voltage/time/KV/event/thread providers are fixtures; actual downstream composition remains open','Selected compiler saved-record registers and event tail boundary verified; other compilers/LTO require revalidation','Runtime/handle initialization, persistence, physical timing/concurrency, canonical admission and original image identity remain gates']),indent=2)+'\n');print('Battery low:',comparisons,counts,outcomes)
if __name__=='__main__':main()

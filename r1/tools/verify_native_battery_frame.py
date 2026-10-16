#!/usr/bin/env python3
"""Six-byte frame, two connection reads, raw return and restored12-byte record."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-frame';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_glasses_connection_handle_get':0x4cb34,'r1_ble_tx_queue_dispatch_type0':0x34064}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_frame.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 p=OUT/'rea-913fc.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-913fc-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==62;evidence[p.name]=sha(p)
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x913fc&length=62']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x913fc-0x27000:0x913fc-0x27000+62];p=OUT/'ghidra-body.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 machines=[];states={};counts={'comparisons':0,'connection_reads':0,'sends':0,'sentinel':0}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   if a not in kinds:
    if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   f=states[id(u)];n=kinds[a]
   if n=='r1_glasses_connection_handle_get':value=f['handles'][f['reads']];f['reads']+=1;event=(n,value)
   else:
    args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];assert args[0]==f['handles'][1] and args[2]==6;data=bytes(u.mem_read(args[1],12));assert data==f['record'];event=(n,args[0],data,args[2]);f['sends']+=1;value=f['raw']
    if f['mutation']:f['record']=bytes((i*31+7)&255 for i in range(12));u.mem_write(args[1],f['record'])
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=itertools.chain(((level,state,(1,2),0x80000007,False) for level,state in itertools.product(range(256),range(256))),itertools.product((0,1,255,256,0xffffffff),(0,1,255,256,0xffffff01),((0xffff,0),(0,0xffff),(0xffff0000,1),(0xffffffff,0xffffffff),(1,2)),(0,1,0x80000000,0xffffffff),(False,True)))
  for level,state,handles,raw,mutation in cases:
   results=[];sent=handles[0]!=0xffff;expected=raw if sent else 0xffff
   for candidate,u in enumerate(machines):
    record=struct.pack('<III',0x008b0900,(level&255)|((state&255)<<8),0);states[id(u)]={'record':record,'handles':handles,'raw':raw,'mutation':mutation,'trace':[],'reads':0,'sends':0};u.reg_write(UC_ARM_REG_R0,level);u.reg_write(UC_ARM_REG_R1,state);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_glasses_tag_frame_send'] if candidate else 0x913fc)|1,0x20000100,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    f=states[id(u)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert regs==list(struct.unpack('<3I',f['record'])) and u.reg_read(UC_ARM_REG_R0)==expected and f['reads']==1+int(sent) and f['sends']==int(sent);results.append((f['trace'],regs))
   assert results[0]==results[1];counts['comparisons']+=1;counts['connection_reads']+=1+int(sent);counts['sends']+=int(sent);counts['sentinel']+=int(not sent)
 vp.write_text(json.dumps(dict(**counts,all_payload_byte_pairs=True,full_r1_r2_r3_checked=True,raw_return_checked=True,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Connection and queue-dispatch endpoints are fixtures; actual lower queue/BLE composition remains open','Selected compiler three-word return-register restoration verified; other compilers/LTO require revalidation','Connection/state initialization, physical delivery and original image identity remain gates']),indent=2)+'\n');print('Battery frame:',counts)
if __name__=='__main__':main()

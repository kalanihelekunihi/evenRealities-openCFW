#!/usr/bin/env python3
"""Native config getters with direct partial writes or actual cached-class/musl copy."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-configuration';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SLOT=0x20007df8;NODE=0x20001000;PORT=0x20000800;PORT2=0x20000880;PORT_SLOT=0x20006974
ENTRIES={'r1_batcfg_byte0_get':(0x7bb44,20),'r1_batcfg_flag1_get':(0x7bb5c,26),'r1_batcfg_word1_signed_get':(0x7bb7c,20)}
def main():
 real='--real-kv' in sys.argv;vp=OUT/('kv-integration-verification.json' if real else 'verification.json');vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_configuration.o';assert sha(obj)==r['units'][0]['object_sha256'];objects=[obj];providers={}
 for path,h in r['inputs'].items():assert sha(ROOT/path)==h,path
 if real:
  kr=BASE/'native-kv-class/report.json';q=json.loads(kr.read_text());ko=kr.parent/'native_kv_class.o';assert sha(ko)==q['units'][0]['object_sha256'];objects.append(ko);providers['native-kv-class/report.json']=sha(kr)
  for path,h in q['inputs'].items():assert sha(ROOT/path)==h,path
  mr=BASE/'runtime/report.json';mo=mr.parent/'memory-runtime.o';assert sha(mo)==json.loads(mr.read_text())['relocatable_sha256'];objects.append(mo);providers['runtime/report.json']=sha(mr)
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';apphash=sha(app);assert apphash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for name,(a,z) in ENTRIES.items():
  p=OUT/f'rea-{a:x}.json';p.write_bytes((BASE/'native-battery-runtime'/f'rea-next-{a:x}-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==z and q['normalized_result']['entrypoint']==hex(a);evidence[p.name]=sha(p)
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length=32']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+32];p=OUT/f'ghidra-{a:x}.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 counts={n:0 for n in ENTRIES};machines=[];states={};kv_counts={'native':0,'source':0};callback_counts={'native':0,'source':0}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  bindings=['--defsym=r1_batcfg_record_kv_handle='+hex(SLOT)]+(['--defsym=r1_kv_port='+hex(PORT_SLOT),'--defsym=r1_health_record_kv_handle=0x20007df4'] if real else ['--defsym=r1_kv_class_read=0x1100001'])
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),*bindings,*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def hook(u,a,size,_):
   side='source' if u is machines[1] else 'native';f=states[id(u)]
   if a in (0x73930,syms.get('r1_kv_class_read',0x1100001)&~1):
    kv_counts[side]+=1;args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];assert args[0]==NODE and args[2]==4
    before=struct.unpack('<I',bytes(u.mem_read(args[1],4)))[0];assert before==f['seed'];f['trace'].append(('read',args[0],4,before))
    if real:return
    if f['width']:u.mem_write(args[1],struct.pack('<I',f['payload'])[:f['width']])
    u.reg_write(UC_ARM_REG_R0,f['payload']%3 and 0xffffffff);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a in (0x1100100,0x1100110,0x1100120):
    callback_counts[side]+=1;name={0x1100100:'enter',0x1100110:'leaveA',0x1100120:'leaveB'}[a];f['trace'].append((name,))
    if name=='enter' and f['mutation']:
     u.mem_write(NODE+24,struct.pack('<I',f['payload']^0xa5a5a5a5));u.mem_write(NODE+20,struct.pack('<H',65535));u.mem_write(PORT_SLOT,struct.pack('<I',PORT2))
    u.reg_write(UC_ARM_REG_R0,0xffffffff);u.reg_write(UC_ARM_REG_R3,0x87654321);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if side=='source' and a<0x1000000 and a!=0x20000100:raise AssertionError(('source used native provider',hex(a)))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=[]
  if real:
   cases=itertools.product(ENTRIES,[(n<<16)|(255-n) for n in range(256)],(0,0x123456a5,0xffffffff),(0,3,4,5,65535),(False,True))
  else:
   cases=itertools.chain(((n,(v<<16)|(v&255),0x123456a5,4,False) for n in ENTRIES for v in range(65536)),itertools.product(ENTRIES,(0,0x12345678,0x8000ff00,0xffffffff),(0,0x123456a5,0xffffffff),(0,1,2,4),(False,)))
  for name,payload,seed,size_or_width,mutation in cases:
   width=0 if real and size_or_width!=4 else 4 if real else size_or_width
   word=(payload^0xa5a5a5a5) if real and width and mutation else payload if width==4 else ((seed&(~((1<<(width*8))-1)&0xffffffff))|(payload&((1<<(width*8))-1))) if width else seed
   expected=word&255 if name=='r1_batcfg_byte0_get' else int(word>>16!=0) if name=='r1_batcfg_flag1_get' else ((word>>16)|0xffff0000 if word&0x80000000 else word>>16)
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'seed':seed,'payload':payload,'width':width,'mutation':mutation};u.mem_write(SLOT,struct.pack('<I',NODE));u.mem_write(NODE,bytes(40));u.mem_write(NODE+20,struct.pack('<H',size_or_width if real else 4));u.mem_write(NODE+24,struct.pack('<I',payload));u.mem_write(PORT_SLOT,struct.pack('<I',PORT));u.mem_write(PORT,bytes(28)+struct.pack('<II',0x1100101,0x1100111));u.mem_write(PORT2,bytes(28)+struct.pack('<II',0x1100101,0x1100121))
    for reg,value in [(UC_ARM_REG_R3,seed),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=2000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    assert u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_R3)==word,(name,payload,seed,size_or_width,mutation,candidate,hex(u.reg_read(UC_ARM_REG_R0)),hex(expected),hex(u.reg_read(UC_ARM_REG_R3)),hex(word))
    results.append((states[id(u)]['trace'],bytes(u.mem_read(NODE,40)),bytes(u.mem_read(PORT_SLOT,4))))
   assert results[0]==results[1];counts[name]+=1
 assert kv_counts['native']==kv_counts['source']==sum(counts.values()) and callback_counts['native']==callback_counts['source']
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,actual_kv_class_and_memory=real,kv_entry_counts=kv_counts,port_callback_counts=callback_counts,full_r3_checked=True,provider_reports=providers,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=apphash,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Selected incoming/return r3 transfer verified; other compiler/LTO settings require revalidation','KV handle/port records are fixtures; cached read and musl copy execute in real-KV mode, callbacks remain modeled','Handle/state initialization, persistence, full startup and original instruction/image identity remain open']),indent=2)+'\n');print('Battery configuration:',counts,kv_counts,callback_counts)
if __name__=='__main__':main()

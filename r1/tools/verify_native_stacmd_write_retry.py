#!/usr/bin/env python3
"""Native retry/log short-circuit/counter contracts with explicit lower providers."""
import csv,hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-stacmd-write-retry';F=0x200075c0;B=0x20003000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_stacmd_bus_recovery_native':0x5cc8c,'r1_stacmd_write_frame_native':0x28c6c,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_stacmd_write_retry.o'
 assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x35698&length=200']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x35698-0x27000:0x35760-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 row=next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x00035698');(OUT/'evidence.json').write_text(json.dumps(dict(ownership_row=row,locked_ownership_changed=False,rea_structured_metadata_obtained=False,rea_limitation='procedure_info invalid_request: No procedure exists at requested address0x35698 in current REA analysis; native Ghidra-MCP bytes and locked row used',attempts=9,counter=hex(F),ring_descriptor='0x3570c',sdk_descriptor='0x3573c'),indent=2)+'\n')
 count=0;rng=random.Random(0x35698);section_hashes={};sequences=[(i,) for i in range(8)]+[(0,4,2),(1,2),(4,0,7,0),(0,0,0,1,7),(0xffffffff,0)]
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .ring 0x3570c : { *(.r1.stacmd_retry.ring) } .sdk 0x3573c : { *(.r1.stacmd_retry.sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_stacmd_failed_transactions='+hex(F),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  sections=[]
  for name,address in [('ring',0x3570c),('sdk',0x3573c)]:
   file=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(file)],check=True);data=file.read_bytes();assert data==app.read_bytes()[address-0x27000:address-0x27000+len(data)];sections.append((address,data));section_hashes[name]={'address':address,'bytes':len(data),'sha256':sha(file)}
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   if a not in kinds:
    if id(u)==id(machines[1]) and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
    return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
   if n=='r1_structured_log_mode_get':value=f['sequence'][f['mode_index']%len(f['sequence'])];f['mode_index']+=1;event=('mode',value)
   elif n=='r1_stacmd_bus_recovery_native':f['attempt']+=1;event=('recovery',f['attempt'])
   elif n=='r1_stacmd_write_frame_native':assert r==[0x44,f['reg'],f['length'],B];event=('frame',*r);value=f['raw_result'] if f['attempt']==f['success'] else 0
   elif n=='r1_structured_log_format':assert r[:3]==[0xc400000,0x3570c,0x3570c];event=('ring',*r)
   else:assert r[:2]==[0x1c0003,0x3573c];event=('sdk',*r[:3])
   f['trace'].append(event)
   if f['mutation'] and n!='r1_structured_log_mode_get':u.mem_write(F,struct.pack('<I',0xffffffff))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  for address,data in sections:machines[1].mem_write(address,data)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for sequence,success,pair,raw_result,mutation in itertools.product(sequences,range(11),[(0,0),(255,1),(0xffffffff,0xffffffff)],(1,0x80000000,0xffffffff),(False,True)):
   reg,length=pair;counter=rng.choice((0,0xffffffff,rng.getrandbits(32)));results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'attempt':0,'mode_index':0,'sequence':sequence,'reg':reg,'length':length,'raw_result':raw_result,'success':success,'mutation':mutation};u.mem_write(F-4,struct.pack('<3I',0xaabbccdd,counter,0x11223344));u.reg_write(UC_ARM_REG_R0,reg);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,B);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,r in enumerate(saved):u.reg_write(r,0x12345600+i)
    u.emu_start((syms['r1_stacmd_write_retry_native'] if candidate else 0x35698)|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
    assert states[id(u)]['attempt']==(success if 1<=success<=9 else 9)
    assert u.reg_read(UC_ARM_REG_R0)==(raw_result if 1<=success<=9 else 0)
    results.append((states[id(u)]['trace'],bytes(u.mem_read(F-4,12))))
   assert results[0]==results[1],(sequence,success,pair,raw_result,mutation,results);count+=1
 vp.write_text(json.dumps(dict(comparisons=count,mode_sequences=len(sequences),source_descriptor_sections=section_hashes,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['Recovery/write-frame and logger endpoints are fixtures; actual provider composition remains open','Counter is a test binding; typed registration/state ownership unresolved','REA current analysis has no procedure at requested address; locked row and native bytes authenticate','Raw frame return preserved; no physical timing/bus success/whole-image identity claim']),indent=2)+'\n');print('STACMD write retry:',count,'native/source comparisons')
if __name__=='__main__':main()

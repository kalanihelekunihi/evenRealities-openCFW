#!/usr/bin/env python3
"""Native system-track byte/register/log contract through the battery-provider adapter."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-yhm-system-track';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_yhm_system_track_native':(0x355bc,200),'r1_native_charger_initialize':(0x5079c,4)}
P={'r1_yhm_register_read_native':0x3540c,'r1_yhm_register_write_native':0x35760,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_yhm_system_track.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';ghidra={}
 for name,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+name+'.json');p.write_bytes(raw);ghidra[p.name]=sha(p)
 for address,size in [(0x355bc,106),(0x5079c,4)]:
  q=json.loads((OUT/f'rea-{address:x}.json').read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
 rows=[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [0x355bc,0x5079c]];(OUT/'evidence.json').write_text(json.dumps(dict(ownership_rows=rows,locked_ownership_changed=False,register_contract='Capture incoming r2/r3; read word low byte begins0; output word low byte becomes read|2; restore both full words to r2/r3',return_contract='Forward final register-write raw word; battery updater may discard it',logging_contract='Repeated/short-circuit mode reads; descriptor IDs preserved',compiler_gate='Selected target register transfers/noinline/prologue verified; other toolchain/LTO settings require revalidation'),indent=2)+'\n')
 counts={n:0 for n in ENTRIES};sequences=[(i,) for i in range(8)]+[(0,4,2),(1,2),(4,0,7,0),(0,0,0,1,7),(0xffffffff,0)];sections={}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .ring 0x35628 : { *(.r1.yhm_track.ring) } .sdk 0x3565c : { *(.r1.yhm_track.sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  payloads=[]
  for name,address in [('ring',0x35628),('sdk',0x3565c)]:
   path=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(path)],check=True);data=path.read_bytes();assert data==app.read_bytes()[address-0x27000:address-0x27000+len(data)];sections[name]={'address':address,'bytes':len(data),'sha256':sha(path)};payloads.append((address,data))
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,address,size,_):
   if address not in kinds:
    if id(u)==id(machines[1]) and address<0x1000000 and address!=0x20000100:raise AssertionError(('source used native provider',hex(address)))
    return
   f=states[id(u)];name=kinds[address];a=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
   if name=='r1_yhm_register_read_native':
    assert a[:2]==[1,1];before=struct.unpack('<I',bytes(u.mem_read(a[2],4)))[0];assert before==f['incoming3']&0xffffff00;event=('read',1,1,before)
    if f['read_value'] is not None:u.mem_write(a[2],bytes([f['read_value']]))
    value=0xffffffff
   elif name=='r1_yhm_register_write_native':assert a[:2]==[1,1];word=struct.unpack('<I',bytes(u.mem_read(a[2],4)))[0];assert word==f['out2'];event=('write',1,1,word);value=f['write_result']
   elif name=='r1_structured_log_mode_get':value=f['sequence'][f['mode_index']%len(f['sequence'])];f['mode_index']+=1;event=('mode',value)
   elif name=='r1_structured_log_format':assert a==[0xc400000,0x35628,0x35628,f['out2']&255];event=('ring',*a)
   else:assert a[:3]==[0x1c0003,0x3565c,f['out2']&255];event=('sdk',*a[:3])
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  for address,data in payloads:machines[1].mem_write(address,data)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,read_value,sequence,write_result,incoming in itertools.product(ENTRIES,(None,*range(256)),sequences,(0,1,0x80000000,0xffffffff),((0,0),(0x123456a5,0x89abcdef),(0xffffffff,0xffffffff))):
   incoming2,incoming3=incoming;byte=read_value if read_value is not None else 0;out2=(incoming2&0xffffff00)|(byte|2);out3=(incoming3&0xffffff00)|byte;results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'mode_index':0,'incoming3':incoming3,'out2':out2,'read_value':read_value,'sequence':sequence,'write_result':write_result};u.reg_write(UC_ARM_REG_R2,incoming2);u.reg_write(UC_ARM_REG_R3,incoming3);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for index,reg in enumerate(saved):u.reg_write(reg,0x12345600+index)
    u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=2000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+index for index in range(8)]
    assert u.reg_read(UC_ARM_REG_R0)==write_result and u.reg_read(UC_ARM_REG_R2)==out2 and u.reg_read(UC_ARM_REG_R3)==out3,(name,read_value,sequence,incoming,hex(u.reg_read(UC_ARM_REG_R2)),hex(out2),hex(u.reg_read(UC_ARM_REG_R3)),hex(out3));results.append(states[id(u)]['trace'])
   assert results[0]==results[1];counts[name]+=1
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,mode_sequences=len(sequences),all_read_bytes=True,no_write_case=True,full_r2_r3_return_checked=True,source_descriptor_sections=sections,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=ghidra,rea_evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['Read/write/logger endpoints are fixtures; actual lower transport/updater composition remains open','Selected register transfers/noinline/prologue verified; other compiler/LTO settings need revalidation','No-read-write byte behavior preserved; raw write return not interpreted as bus success','Full startup, physical GPIO/timing/concurrency and original whole-image byte identity remain open']),indent=2)+'\n');print('YHM system track:',counts)
if __name__=='__main__':main()

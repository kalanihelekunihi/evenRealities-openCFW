#!/usr/bin/env python3
"""Full linked CASE router RAM-only families: actual native/C, no stubs."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
import hashlib,json,random,struct
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;elf=H.parent/'case-wave016-battery-measurement-abi/qualified/case.elf';fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rng=random.Random(0x1e94)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';cases=[];rows=[]
ram_commands={0,7,8,0x13,0x3e,0x46,0x58,0x59,0x5a,0x5b}
for command in range(256):
 if command in ram_commands:continue
 for side in [0,1]:
  for position in range(4):
   for length in [1,2,6,32,255]:
    ram=bytearray(rng.randbytes(0x3000));ram[0xbf]=1;ram[0x895]=1;struct.pack_into('<I',ram,0xe24+0x88,0);p=bytearray(rng.randbytes(0x118));start=position+4;p[position:start]=bytes([0x5a,0xa5,0xff,length]);p[start]=command;p[start+length]=(length-2+sum(p[start:start+length]))&255;ram[0x664:0x77c]=p
    cases.append({'side':side,'position':position,'command':command,'length':length,'ram':bytes(ram)})
for index,c in enumerate(cases):
 pair=[]
 for native in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
  if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
  else:
   for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,c['ram']);u.reg_write(UC_ARM_REG_R0,c['side']);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x2000f001)
  trace=[]
  def observe(uc,address,size,data):
   if address!=(0x080066ac if native else sym['case_write_controller_blocking']&~1):return
   handle=uc.reg_read(UC_ARM_REG_R0);ptr=uc.reg_read(UC_ARM_REG_R1);count=uc.reg_read(UC_ARM_REG_R2);timeout=uc.reg_read(UC_ARM_REG_R3);assert handle==0x20000e24 and count==1 and timeout==65535;trace.append(bytes(uc.mem_read(ptr,1))[0])
  u.hook_add(UC_HOOK_CODE,observe)
  u.emu_start((0x08001e94 if native else sym['case_record_dispatch_1e94'])|1,0x2000f000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x2000f000,('did_not_return',index,native,c['command'],hex(u.reg_read(UC_ARM_REG_PC)))
  assert u.reg_read(UC_ARM_REG_SP)==0x20008000;pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000000,0x3000)),trace))
 assert len(pair[0][2])==len(pair[1][2])==c['length']+5
 if pair[0]!=pair[1]:
  diff=[{'offset':hex(i),'native':a,'source':b,'initial':c['ram'][i]} for i,(a,b) in enumerate(zip(pair[0][1],pair[1][1])) if a!=b];r={'status':'FAIL_NATIVE_C_ROUTER','case_index':index,'case':{k:v for k,v in c.items() if k!='ram'},'native_return':pair[0][0],'source_return':pair[1][0],'RAM_differences':diff,'ELF_sha256':sha(elf)};(H/'failure.json').write_text(json.dumps(r,indent=2)+'\n');(H/'failure-input.bin').write_bytes(c['ram']);raise AssertionError(r)
 rows.append({k:v for k,v in c.items() if k!='ram'})
r={'status':'PASS_FULL_LINKED_ROUTER_BUSY_UART_FORWARDING','cases':len(rows),'ELF_sha256':sha(elf),'firmware_sha256':sha(fw),'comparisons':rows,'limits':['Full actual source graph and native bodies; no child stubs/cuts or hardware models. Loggingdisabled; tenRAM-only commandfamilies plusnoheader andall256opcode badCRC paths through genuine quiethexlogger.','BusyUART sendsnowirebytes; capturedisplaysattempts, not physicaloutput. Ready/transientFIFO/log-enabled paths andwholeCASE remainunvalidated.']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])

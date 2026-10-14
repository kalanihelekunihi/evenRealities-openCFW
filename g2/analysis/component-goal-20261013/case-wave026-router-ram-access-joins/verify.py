#!/usr/bin/env python3
"""Full linked CASE router RAM-only families: actual native/C, no stubs."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
import hashlib,json,random,struct
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;elf=H.parent/'case-wave022-logging-stack/final/case.elf';fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rng=random.Random(0x1e94)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';cases=[];rows=[]
for command in [0x13,0x58,0x71]:
 for side in [0,1]:
  for subtype in [0,1,6,0x20]:
   for badcrc in [False,True]:
    ram=bytearray(rng.randbytes(0x3000));ram[0xbf]=0;ram[0x895]=1;struct.pack_into('<I',ram,0xe24,0x40013800);struct.pack_into('<I',ram,0xe24+8,0);struct.pack_into('<I',ram,0xe24+16,0);struct.pack_into('<I',ram,0xe24+0x88,0x20);p=bytearray(rng.randbytes(0x118));length=32;p[:4]=bytes([0x5a,0xa5,0xff,length]);p[4]=command;p[7]=subtype;p[8]=1;p[13]=2;p[14]=0x40;p[4+length]=(length-2+sum(p[4:4+length])+int(badcrc))&255;ram[0x664:0x77c]=p
    cases.append({'side':side,'position':0,'command':command,'length':length,'subtype':subtype,'badcrc':badcrc,'ram':bytes(ram)})
audit=json.loads((H.parent/'case-wave025-ram-callback-provenance/verification.json').read_text());targets={int(x['address'],16) for x in audit['RAM_literals'] if not x['aligned_native_literal_word_locations']};hits={True:{},False:{}}
for index,c in enumerate(cases):
 pair=[]
 for native in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
  if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
  else:
   for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x40013000,0x1000);u.mem_write(0x4001381c,struct.pack('<I',0xc0));u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,c['ram']);u.reg_write(UC_ARM_REG_R0,c['side']);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x2000f001)
  trace=[];MMIO=[]
  def observe(uc,address,size,data):
   if address!=(0x080066ac if native else sym['case_write_controller_blocking']&~1):return
   handle=uc.reg_read(UC_ARM_REG_R0);ptr=uc.reg_read(UC_ARM_REG_R1);count=uc.reg_read(UC_ARM_REG_R2);timeout=uc.reg_read(UC_ARM_REG_R3);assert handle==0x20000e24 and count==1 and timeout==65535;trace.append(bytes(uc.mem_read(ptr,1))[0])
  u.hook_add(UC_HOOK_CODE,observe)
  def writes(uc,access,address,size,value,data):
   if 0x40013000<=address<0x40014000:MMIO.append((address,size,value))
  u.hook_add(UC_HOOK_MEM_WRITE,writes)
  def ram_access(uc,access,address,size,value,data):
   if not 0x20000000<=address<0x20003000:return
   for target in targets:
    if address<=target<address+size:
     key=hex(target);op='read' if access==16 else 'write';example={'address':hex(address),'size':size,'operation':op,'case_index':index,'PC':hex(uc.reg_read(UC_ARM_REG_PC))};entry=hits[native].setdefault(key,{'access_count':0,'examples':[]});entry['access_count']+=1
     if len(entry['examples'])<4:entry['examples'].append(example)
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,ram_access)
  u.emu_start((0x08001e94 if native else sym['case_record_dispatch_1e94'])|1,0x2000f000,count=1000000);assert u.reg_read(UC_ARM_REG_PC)==0x2000f000,('did_not_return',index,native,c['command'],hex(u.reg_read(UC_ARM_REG_PC)))
  assert u.reg_read(UC_ARM_REG_SP)==0x20008000;pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000000,0x3000)),trace,MMIO))
 assert pair[0][3]==[(0x40013828,4,x) for x in pair[0][2]];assert pair[1][3]==[(0x40013828,4,x) for x in pair[1][2]]
 if pair[0]!=pair[1]:
  diff=[{'offset':hex(i),'native':a,'source':b,'initial':c['ram'][i]} for i,(a,b) in enumerate(zip(pair[0][1],pair[1][1])) if a!=b]
  r={'status':'FAIL_NATIVE_SOURCE_LOGGED_ROUTER','case_index':index,'case':{k:v for k,v in c.items() if k!='ram'},'native_return':pair[0][0],'source_return':pair[1][0],'RAM_differences':diff,'native_attempt_hex':bytes(pair[0][2]).hex(),'source_attempt_hex':bytes(pair[1][2]).hex()};(H/'failure.json').write_text(json.dumps(r,indent=2)+'\n');(H/'failure-input.bin').write_bytes(c['ram']);raise AssertionError((index,c['command'],len(pair[0][2]),len(pair[1][2]),diff[:3]))
 rows.append({k:v for k,v in c.items() if k!='ram'})
r={'status':'PASS_BOUNDED_ROUTER_RAM_ACCESS_JOINS','cases':len(rows),'ELF_sha256':sha(elf),'firmware_sha256':sha(fw),'comparisons':rows,'RAM_access_joins':{'native':hits[True],'source':hits[False]},'derived_targets_both_exercised':sorted(set(hits[True])&set(hits[False])),'derived_targets_unjoined':sorted(hex(x) for x in targets if hex(x) not in hits[True] or hex(x) not in hits[False]),'limits':['Actual native/source router/logger/formatter/callback/UART bodies execute; no child cuts or return injection','Synthetic static ready ISR; not physical UART/FIFO/timing proof','Bounded charging/version/default/bad-CRC cases; no global callback reachability claim']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])

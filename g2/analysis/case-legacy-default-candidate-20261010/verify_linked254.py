#!/usr/bin/env python3
"""Linked bounded dispatcher vs stock entry across 254 opcodes and lengths."""
from pathlib import Path
import hashlib,json,struct
from collections import Counter
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];image=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(image).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=image[32:];elf=D/'linked254.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock={0x08006b98:'gpio4',0x08006b80:'gpio0',0x08009170:'log',0x08002f60:'fill',0x080067c8:'hex',0x08009ff0:'value_a',0x08009f18:'value_b',0x0800a01e:'value_c',0x08003664:'set_sn',0x0800d1bc:'aa_first',0x0800d218:'aa_second',0x08003558:'ab_child',0x0800a888:'b0_child',0x080039e4:'pmic',0x08002c8e:'watchdog'}
source={0x0010f000:'gpio4',0x0010f100:'gpio0',0x0010f200:'log',0x0010f300:'fill',0x0010f400:'hex',0x0010f500:'value_a',0x0010f600:'value_b',0x0010f700:'value_c',0x0010f800:'set_sn',0x0010f900:'aa_first',0x0010fa00:'aa_second',0x0010fb00:'ab_child',0x0010fc00:'b0_child',0x0010fd00:'pmic',0x0010fe00:'watchdog'}
def readz(u,p):
 b=bytearray()
 while len(b)<160:
  c=u.mem_read(p+len(b),1)[0]
  if not c:break
  b.append(c)
 return b.decode()
def fmtargs(uc,fmt):
 if fmt=='%02x%02x%02x%02x%02x%02x%02x%02x' or fmt.count('%d')==8:
  return [uc.reg_read(r) for r in [UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]+list(struct.unpack('<5I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),20))))
 if fmt.count('%d')==3:return [uc.reg_read(r) for r in [UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
 if '%s' in fmt and '%d' in fmt:return [readz(uc,uc.reg_read(UC_ARM_REG_R1)),uc.reg_read(UC_ARM_REG_R2)]
 if '%s' in fmt:return [readz(uc,uc.reg_read(UC_ARM_REG_R1))]
 if '%d' in fmt or '%02x' in fmt:return [uc.reg_read(UC_ARM_REG_R1)]
 return []
rows=[]
for opcode in range(256):
 if opcode in [0xee,0xff]:continue
 for length in [0,1,2,4,8]:
  for flag in [0,1]:
   pair=[]
   for original in [True,False]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
    for address,data in segments:u.mem_write(address,data)
    u.mem_write(0x20004000,bytes([opcode,0x55,0x66,0x77,0x88])+bytes(27));u.mem_write(0x200000bd,bytes([0,0,flag,0,0,0,0,0,0]));u.mem_write(0x200000f0,(0x20004500).to_bytes(4,'little'));u.mem_write(0x20000105,b'\x00');u.mem_write(0x2000087c,bytes([0,11,0,33,44]+[0]*11+[66,77]+[0]*14));u.mem_write(0x20000884,(0x12345678).to_bytes(4,'little'));u.mem_write(0x20000888,(0x87654321).to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,0x20005000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
    events=[];writes=[];mapping=stock if original else source
    def code(uc,address,size,user):
     if address not in mapping:return
     name=mapping[address];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
     if name=='log':events.append([name,readz(uc,r0),fmtargs(uc,readz(uc,r0))]);uc.reg_write(UC_ARM_REG_R0,0)
     elif name=='fill':uc.mem_write(r0,bytes(range(8)));events.append([name]);uc.reg_write(UC_ARM_REG_R0,0)
     elif name=='hex':events.append([name,r1,bytes(uc.mem_read(r0,r1)).hex()]);uc.reg_write(UC_ARM_REG_R0,0)
     elif name.startswith('value_'):
      val={'value_a':0x11111111,'value_b':0x22222222,'value_c':0x33333333}[name];uc.mem_write(r0,val.to_bytes(4,'little'));events.append([name]);uc.reg_write(UC_ARM_REG_R0,0)
     elif name=='set_sn':events.append([name,bytes(uc.mem_read(r0,16)).hex()]);uc.reg_write(UC_ARM_REG_R0,0x1234)
     elif name in ['gpio4','gpio0','aa_first','aa_second','ab_child','watchdog']:events.append([name,r0]);uc.reg_write(UC_ARM_REG_R0,0x1234)
     else:events.append([name,r0,r1]);uc.reg_write(UC_ARM_REG_R0,0x1234)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    def write(uc,access,address,size,value,user):
     if not 0x20007000<=address<0x20008000 and address!=0x20005000:writes.append([address,size,value])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start((0x08000928 if original else sym['case_legacy_known_dispatch'])|1,0x20001000,count=30000)
    ret=u.reg_read(UC_ARM_REG_R0) if original else int.from_bytes(u.mem_read(0x20005000,4),'little')
    handled=1 if original else u.reg_read(UC_ARM_REG_R0)
    pair.append(dict(return_value=ret,handled=handled,events=events,writes=writes,state=bytes(u.mem_read(0x200000bd,9)).hex()))
   assert pair[1]['handled']==1,(opcode,length,flag,pair)
   if {k:v for k,v in pair[0].items() if k!='handled'}!={k:v for k,v in pair[1].items() if k!='handled'}:
    (D/'linked254-failure.json').write_text(json.dumps(dict(opcode=opcode,length=length,flag=flag,pair=pair),indent=2)+'\n');raise AssertionError((opcode,length,flag,pair))
   rows.append(dict(opcode=opcode,length=length,flag=flag,events=pair[0]['events']))
out=dict(status='PASS_LINKED_254_BOUNDED_ROUTES',cases=len(rows),opcodes=254,image_sha256=sha,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['ee and ff omitted: only prefixes to nonreturn lower calls are proven.','Controlled lower calls do not prove GPIO, PMIC, watchdog, logging, reset or standby effects.','32-byte command allocation even for logical length zero; dd byte-1 physical short-frame safety remains open.'],rows=rows)
(D/'linked254-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))

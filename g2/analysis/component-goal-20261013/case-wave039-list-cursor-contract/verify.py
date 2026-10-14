#!/usr/bin/env python3
"""Actual nativeuxListRemove vs recovered shared CASE helper, valid list cursors."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,subprocess,argparse
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;A=argparse.ArgumentParser();A.add_argument('--checkpoint',default='case-wave033-native-timer-message-width');A.add_argument('--label',default='before');args=A.parse_args();P=H.parent/args.checkpoint;F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';E=H/(args.label+'-fixture.elf');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cmd=json.loads((P/'final/receipt.json').read_text())['link_command'].copy();cmd.insert(1,'-ucase_source_list_remove');cmd[-1]=str(E);subprocess.run(cmd,check=True)
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
LIST=0x20002000;SP=0x20002c88;STOP=0x2000f000;rows=[]
def run(native,count,index,removed):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 items=[0x20002100+i*0x40 for i in range(count)];nodes=[LIST+8]+items;item=items[removed]
 w(LIST,count);w(LIST+4,LIST+8 if index==-1 else items[index]);w(LIST+8,0xffffffff)
 for i,node in enumerate(nodes):w(node+4,nodes[(i+1)%len(nodes)]);w(node+8,nodes[(i-1)%len(nodes)])
 for i,node in enumerate(items):w(node,100+i);w(node+12,0x20002500+i*0x40);w(node+16,LIST)
 previous=struct.unpack('<I',bytes(u.mem_read(item+8,4)))[0];saved=[0x45670000+i for i in range(8)]
 for r,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_R0,item);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start((0x0800bf2c if native else sy['case_source_list_remove'])|1,STOP,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
 assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
 ram=bytes(u.mem_read(0x20000000,0x2888));cursor=struct.unpack_from('<I',ram,0x2004)[0]
 return {'return':u.reg_read(UC_ARM_REG_R0),'ram':ram.hex(),'cursor':hex(cursor),'expected_cursor':hex(previous if index==removed else LIST+8 if index==-1 else items[index])}
for count in [1,2,3,5]:
 for index in range(-1,count):
  for removed in range(count):
   a=run(True,count,index,removed);b=run(False,count,index,removed)
   assert a['return']==count-1 and a['cursor']==a['expected_cursor']
   if a!=b:
    (H/(args.label+'-failure.json')).write_text(json.dumps({'count':count,'cursor_index':index,'removed_index':removed,'native':a,'source':b},indent=2)+'\n');raise AssertionError((count,index,removed,a['cursor'],b['cursor']))
   rows.append({'count':count,'cursor_index':index,'removed_index':removed,'result_cursor':a['cursor']})
r={'status':'PASS_NATIVE_LIST_REMOVE_CURSOR_PREVIOUS_CONTRACT','cases':len(rows),'fixture_ELF_sha256':sha(E),'production_ELF_sha256':sha(P/'final/case.elf'),'firmware_sha256':sha(F),'link_command':cmd,'comparisons':rows,'limits':['Valid linked circular lists and native/source direct bodies; no stubs/providercuts','Fixtures pin FreeRTOS list/item layout; not concurrent modification/IRQ behavior','RAM comparison excludes native1024byte stackwindow; SP/callee-saved restored']};(H/(args.label+'-verification.json')).write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])

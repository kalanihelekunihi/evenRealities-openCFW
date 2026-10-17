#!/usr/bin/env python3
"""Native/source FAL cache lookup: inclusive bounds, unaligned pointers and asserts."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-fal-device-lookup';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;TABLE=0x20002000;STATE=0x200077b8;CACHE=0x2001e544
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 obj=OUT/'native_fal_device_lookup.o';stateobj=OUT/'shared-state.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts={'returned':0,'lower_assert':0,'upper_assert':0,'unaligned_returned':0}
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS { .lookup 0x64f74 : { *(.text.r1_fal_native_device_by_partition) } .name 0x9c43f : { *(.r1.fal.lookup_name) } .table 0x200077b8 (NOLOAD) : { *(.bss.r1_fal_partition_table) } .count 0x200077bc (NOLOAD) : { *(.bss.r1_fal_partition_count) } .cache 0x2001e544 (NOLOAD) : { *(.bss.r1_fal_partition_cache) } /DISCARD/ : { *(.ARM.exidx*) } }\nr1_native_printf = 0x38061;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(stateobj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacement=[]
  for sec,a,length in [('lookup',0x64f74,180),('name',0x9c43f,26)]:
   p=td/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();assert len(d)==length and d==image[a-0x27000:a-0x27000+length];replacement.append((a,d))
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3}
  assert [syms[n] for n in ['r1_fal_partition_table','r1_fal_partition_count','r1_fal_partition_cache']]==[STATE,STATE+4,CACHE]
  def hook(u,a,size,_):
   s=states[id(u)]
   if a in [0x64f88,0x64fa0]:s['assert']=hex(a);u.emu_stop()
   if a==0x38060:
    r=[u.reg_read(x) for x in REGS];s['trace'].append([r,bytes(u.mem_read(r[0],100)).split(b'\0')[0].decode()]);u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0xa1);u.reg_write(UC_ARM_REG_R2,0xa2);u.reg_write(UC_ARM_REG_R3,0xa3);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacement:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=list(itertools.product([0,1,2,3,4,5,6,7,8,9],range(-65,514),[0,1,0xffffffff]))
  for count,offset,cacheword in cases:
   part=TABLE+offset;expected_assert='0x64f88' if part<TABLE else '0x64fa0' if part>((TABLE+(count<<6)-64)&0xffffffff) else None;outputs=[]
   for u in machines:
    u.mem_write(STATE-4,b'\x96'*12);u.mem_write(STATE,struct.pack('<II',TABLE,count));u.mem_write(CACHE-16,b'\x69'*80)
    for i in range(10):u.mem_write(CACHE+i*4,struct.pack('<I',(cacheword+i*0x100)&0xffffffff))
    u.mem_write(SP-128,b'\x96'*256)
    for r,v in zip(REGS,[part,0xabcdef01,0x98765432,0xfedcba98]):u.reg_write(r,v)
    for i,r in enumerate(SAVED):u.reg_write(r,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(trace=[],**{'assert':None});states[id(u)]=s;u.emu_start(0x64f75,0x20000100,count=1000);assert s['assert']==expected_assert,(count,offset,s)
    if not expected_assert:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(r) for r in SAVED]==[0x12340000+i for i in range(8)] and u.reg_read(UC_ARM_REG_R0)==(cacheword+(offset>>6)*0x100)&0xffffffff
    outputs.append([[u.reg_read(r) for r in REGS],u.reg_read(UC_ARM_REG_SP),s,bytes(u.mem_read(STATE-4,12)).hex(),bytes(u.mem_read(CACHE-16,80)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1],(count,offset,cacheword);counts['lower_assert' if expected_assert=='0x64f88' else 'upper_assert' if expected_assert else 'returned']+=1;counts['unaligned_returned']+=int(not expected_assert and offset%64!=0);digest.update(json.dumps([count,offset,cacheword,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=len(cases),counts=counts,trace_sha256=digest.hexdigest(),object_sha256=sha(obj),shared_state_object_sha256=sha(stateobj),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),native_lookup_executes_with_actual_initializer_owned_state_sections=True,printf_is_fixture=True,cache_words_are_runtime_fixtures=True,inclusive_range_and_unaligned_floor_index_independent_oracle=True,final_table_count_adjacency_is_not_yet_linked_image_proof=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'direct-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

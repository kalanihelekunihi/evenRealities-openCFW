#!/usr/bin/env python3
"""Native-placement byte proof and bounded FlashDB count execution contracts."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-flashdb-query-count';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 obj=OUT/'native_flashdb_query_count.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 sections=[('count',0x63cb4,139),('callback',0x87428,18),('path',0x3f014,14)];digest=hashlib.sha256();exact=[];states={};sp=0x2003d000;db=0x20010000;regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS { .count 0x63cb4 : { *(.text.r1_fdb_native_query_count) } .callback 0x87428 : { *(.text.r1_fdb_native_query_count_cb) } .path 0x3f014 : { *(.text.r1_fdb_native_db_path) } /DISCARD/ : { *(.ARM.exidx*) } }\nr1_native_printf = 0x38061; r1_health_sync_provider_00063ad8 = 0x63ad9;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE)
  replacements=[]
  for name,addr,length in sections:
   p=td/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();assert len(data)==length and data==image[addr-0x27000:addr-0x27000+length],name;replacements.append((addr,data));exact.append(dict(section=name,address=hex(addr),length=length,sha256=sha(p)))
  machines=[]
  def hook(u,a,size,_):
   state=states[id(u)]
   if a==0x38060:
    r=[u.reg_read(x) for x in regs];p=r[0];text=bytes(u.mem_read(p,100)).split(b'\0')[0].decode();state['trace'].append(['printf',r,text]);u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0xa1);u.reg_write(UC_ARM_REG_R2,0xa2);u.reg_write(UC_ARM_REG_R3,0xa3);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   if a==0x63ad8:
    args=[u.reg_read(x) for x in regs];frame=u.reg_read(UC_ARM_REG_SP);arg=struct.unpack('<I',u.mem_read(frame,4))[0];assert args[3]==0x87429 and arg==sp-20;state['trace'].append(['iterator',args,arg,bytes(u.mem_read(arg,8)).hex()]);u.mem_write(arg+4,struct.pack('<I',state['count']));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for addr,data in replacements:u.mem_write(addr,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=0
  for init,status,count,filemode in itertools.product([0,1,2,255],range(256),[0,1,0x80000000,0xffffffff],[0,1]):
   results=[]
   for u in machines:
    data=bytearray(b'\x96'*256);struct.pack_into('<I',data,0,db+128);struct.pack_into('<I',data,8,db+160);data[24]=init;data[25]=filemode;data[128:133]=b'logs\0';data[164:169]=b'path\0';u.mem_write(db,bytes(data));u.mem_write(sp-256,b'\x96'*512)
    for r,v in zip(regs,[db,0x80000000,0x7fffffff,0xaabbcc00|status]):u.reg_write(r,v)
    for i,r in enumerate(saved):u.reg_write(r,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x20000101);state=dict(trace=[],count=count);states[id(u)]=state;u.emu_start(0x63cb5,0x20000100,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==sp and [u.reg_read(r) for r in saved]==[0x12340000+i for i in range(8)]
    assert u.reg_read(UC_ARM_REG_R0)==(count if init else 0)
    assert len(state['trace'])==(1 if init else 3)
    results.append([[u.reg_read(r) for r in regs],state['trace'],bytes(u.mem_read(db,256)).hex(),bytes(u.mem_read(sp-256,512)).hex()])
   assert results[0]==results[1],(init,status,count,filemode);digest.update(json.dumps([init,status,count,filemode,results[0]],sort_keys=True).encode());cases+=1
 receipt=dict(comparisons=cases,exact_spans=exact,exact_bytes=sum(x['length'] for x in exact),trace_sha256=digest.hexdigest(),source_sha256=sha(ROOT/'r1/components/runtime/native_flashdb_query_count.c'),object_sha256=sha(obj),report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),actual_source_db_path_executed=True,iterator_and_printf_are_fixtures=True,iterator_callback_execution_verified=False,native_address_external_bindings_are_verification_only=True,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

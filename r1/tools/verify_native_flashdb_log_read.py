#!/usr/bin/env python3
"""Direct native/source log-read, short-read history and status-table contracts."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-flashdb-log-read';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DB=0x20010000;TSL=DB+128;TABLE=DB+256;BUFFER=DB+320
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def status(data,n):return next((i+1 for i in range(n-2,-1,-1) if data[i*4]==0),0)
def main():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();obj=OUT/'native_flashdb_log_read.o';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';counts={'status':0,'flash_read':0,'log_read':0};digest=hashlib.sha256();states={}
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS { .read 0x87e14 : { *(.text.r1_fdb_native_read_tsl) } .flash 0x3f03e : { *(.text.r1_fdb_native_flash_read) } .status 0x3f076 : { *(.text.r1_fdb_native_get_status) } /DISCARD/ : { *(.ARM.exidx*) } }\nr1_fdb_native_partition_read = 0x631e9;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,length in [('read',0x87e14,68),('flash',0x3f03e,28),('status',0x3f076,30)]:
   p=td/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();assert len(d)==length and d==image[a-0x27000:a-0x27000+length];replacements.append((a,d))
  def hook(u,a,size,_):
   if a!=0x631e8:return
   s=states[id(u)];r=[u.reg_read(x) for x in REGS];assert r==[DB+400,0x12345678,s['dest'],32];s['trace'].append(r);u.mem_write(r[2],s['payload'][:s['written']]);u.reg_write(UC_ARM_REG_R0,s['result']);u.reg_write(UC_ARM_REG_R1,0x11111111);u.reg_write(UC_ARM_REG_R2,0x22222222);u.reg_write(UC_ARM_REG_R3,0x33333333);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  def run(kind,args,table=b'\xff'*32,written=32,result=32,mode=0,fill=0x96,maxlen=99):
   outputs=[]
   for side,u in enumerate(machines):
    u.mem_write(DB,b'\x69'*512);u.mem_write(DB+8,struct.pack('<I',DB+400));u.mem_write(DB+25,bytes([mode]));u.mem_write(DB+88,struct.pack('<I',maxlen));u.mem_write(TSL+12,struct.pack('<I',0x12345678));u.mem_write(TABLE,table);u.mem_write(SP-256,bytes([fill])*512)
    for r,v in zip(REGS,args):u.reg_write(r,v)
    for i,r in enumerate(SAVED):u.reg_write(r,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(trace=[],payload=table,written=written,result=result,dest=BUFFER if kind=='flash_read' else SP-48);states[id(u)]=s
    u.emu_start({'status':0x3f077,'flash_read':0x3f03f,'log_read':0x87e15}[kind],0x20000100,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(r) for r in SAVED]==[0x12340000+i for i in range(8)]
    if kind=='status':assert u.reg_read(UC_ARM_REG_R0)==status(table,args[1])
    elif kind=='flash_read':assert u.reg_read(UC_ARM_REG_R0)==(2 if mode or result&0x80000000 else 0) and len(s['trace'])==(0 if mode else 1)
    else:
     actual=bytes([fill])*32 if mode else table[:written]+bytes([fill])*(32-written);st=status(actual,6);expected=(maxlen,0xffffffff,0) if st in [0,1] else (int.from_bytes(actual[24:28],'little'),int.from_bytes(actual[28:32],'little'),int.from_bytes(actual[20:24],'little'));assert u.reg_read(UC_ARM_REG_R0)==0 and bytes(u.mem_read(TSL,1))==bytes([st]);assert (int.from_bytes(u.mem_read(TSL+8,4),'little'),int.from_bytes(u.mem_read(TSL+16,4),'little'),int.from_bytes(u.mem_read(TSL+4,4),'little'))==expected
    outputs.append([[u.reg_read(r) for r in REGS],s['trace'],bytes(u.mem_read(DB,512)).hex(),bytes(u.mem_read(SP-256,512)).hex()])
   assert outputs[0]==outputs[1],(kind,args,written,result,mode,fill);counts[kind]+=1;digest.update(json.dumps([kind,args,table.hex(),written,result,mode,fill,maxlen,outputs[0]],sort_keys=True).encode())
  for n,mask,variant in itertools.product(range(1,9),range(128),[1,0x80,255]):
   table=bytearray([variant]*32)
   for i in range(7):table[i*4]=0 if mask>>i&1 else variant
   run('status',[TABLE,n,0xabcdef01,0x98765432],bytes(table))
  for mode,result,written in itertools.product(range(256),[0,1,31,32,0x7fffffff,0x80000000,0xffffffff],[0,1,31,32]):run('flash_read',[DB,0x12345678,BUFFER,32],bytes(range(32)),written,result,mode)
  for mask,written,result,mode,fill in itertools.product(range(32),range(33),[0,32,0xffffffff],[0,1],[0,0x96,255]):
   table=bytearray(b'\xff'*32)
   for i in range(5):table[i*4]=0 if mask>>i&1 else 255
   struct.pack_into('<III',table,20,0x80000001,0x12345678,0x89abcdef);run('log_read',[DB,TSL,0xabcdef01,0x98765432],bytes(table),written,result,mode,fill)
 receipt=dict(comparisons=sum(counts.values()),counts=counts,trace_sha256=digest.hexdigest(),object_sha256=sha(obj),source_sha256=sha(ROOT/'r1/components/runtime/native_flashdb_log_read.c'),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),report_sha256=sha(OUT/'report.json'),partition_read_is_fixture=True,short_read_prefix_lengths_0_through_32_checked=True,all_file_mode_bytes_checked=True,status_decoder_independent_oracle=True,raw_full_private_histories_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'direct-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

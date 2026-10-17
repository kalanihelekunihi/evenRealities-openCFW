#!/usr/bin/env python3
"""Direct source/native sector parse, traversal, partial header and assertion checks."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-flashdb-sector-read';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DB=0x20010000;SEC=DB+128
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def put(data,a,v):struct.pack_into('<I',data,a,v&0xffffffff)
def get(data,a):return int.from_bytes(data[a:a+4],'little')
def status(data,n):return next((i+1 for i in range(n-2,-1,-1) if data[i*4]==0),0)
def main():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';obj=OUT/'native_flashdb_sector_read.o';logobj=BASE/'native-flashdb-log-read/native_flashdb_log_read.o';countobj=BASE/'native-flashdb-query-count/native_flashdb_query_count.o';states={};digest=hashlib.sha256();counts={'returned':0,'assertion_loop':0};spans=[('sector',0x87c24,496,'.text.r1_fdb_native_read_sector'),('name',0x9bdb9,17,'.r1.fdb.sector_function_name'),('read',0x87e14,68,'.text.r1_fdb_native_read_tsl'),('flash',0x3f03e,28,'.text.r1_fdb_native_flash_read'),('status',0x3f076,30,'.text.r1_fdb_native_get_status'),('path',0x3f014,14,'.text.r1_fdb_native_db_path')]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS {'+''.join(' .%s 0x%x : { *(%s) }'%(n,a,s) for n,a,l,s in spans)+' /DISCARD/ : { *(.ARM.exidx*) *(.text.r1_fdb_native_query_count*) } }\nr1_native_printf = 0x38061; r1_fdb_native_partition_read = 0x631e9;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(logobj),str(countobj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacement=[]
  for name,a,length,section in spans:
   p=td/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();assert len(data)==length and data==image[a-0x27000:a-0x27000+length];replacement.append((a,data))
  def hook(u,a,size,_):
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS]
   if a in [0x87c78,0x87d02]:s['assert']=hex(a);u.emu_stop();return
   if a==0x38060:
    s['trace'].append(['log',r,bytes(u.mem_read(r[0],100)).split(b'\0')[0].decode()]);u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0xa1);u.reg_write(UC_ARM_REG_R2,0xa2);u.reg_write(UC_ARM_REG_R3,0xa3)
   elif a==0x631e8:
    assert r[0]==DB+400;s['trace'].append(['partition',r])
    if r[3]==80:assert r[1]==256;u.mem_write(r[2],s['header'][:case['written']]);u.reg_write(UC_ARM_REG_R0,case['result'])
    else:
     assert r[3]==32;slot=(r[1]-336)//32;data=bytearray(b'\xff'*32)
     if slot<3:data[4]=0
     put(data,20,10+slot);put(data,24,case['length']);put(data,28,0x12345678);u.mem_write(r[2],bytes(data));u.reg_write(UC_ARM_REG_R0,case['result'])
   else:return
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,data in replacement:u.mem_write(a,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[dict(sec=sec,end0=e0,end1=e1,traversal=traversal,length=length,written=written,result=result,fill=0x96,null=0,magic=0x304c5354) for sec,e0,e1,traversal,length,written,result in itertools.product(range(4),range(6),range(6),range(2),[0,1,31,128,0xffffffff],[0,16,80],[80,0xffffffff])]
  cases += [dict(sec=2,end0=2,end1=0,traversal=t,length=4,written=w,result=0xffffffff,fill=f,null=0,magic=m) for w,f,t,m in itertools.product(range(81),[0,0x96,255],range(2),[0,0x304c5354])]
  cases += [dict(sec=2,end0=2,end1=0,traversal=0,length=4,written=80,result=80,fill=f,null=1,magic=0x304c5354) for f in [0,0x96,255]]
  for case in cases:
   header=bytearray(b'\xff'*80)
   for off,n,st in [(0,4,case['sec']),(28,6,case['end0']),(56,6,case['end1'])]:
    if st:header[off+(st-1)*4]=0
   for off,value in [(12,case['magic']),(16,0x80000001),(20,101),(24,400),(48,202),(52,432)]:put(header,off,value)
   effective=header[:case['written']]+bytes([case['fill']])*(80-case['written']);expected=bytearray(b'\x69'*40);put(expected,4,256);put(expected,8,get(effective,12));expect_assert=None;expect_return=0
   if case['null']:expect_assert='0x87c78'
   elif get(effective,12)!=0x304c5354:expected[0]=0;expect_return=8
   else:
    expected[0]=1;st=status(effective,4);e0=status(effective[28:],6);e1=status(effective[56:],6);expected[1]=st;expected[24]=e0;expected[25]=e1;put(expected,12,get(effective,16))
    if e0==2:put(expected,16,get(effective,20));put(expected,20,get(effective,24))
    elif e1==2:put(expected,16,get(effective,48));put(expected,20,get(effective,52))
    elif e0==e1==1:expect_assert='0x87d02'
    if not expect_assert:
     empty_idx=336;empty_data=512;remain=176
     if st==2 and case['traversal']:
      for slot in range(3):
       put(expected,16,10+slot);put(expected,20,336+slot*32);empty_idx=(empty_idx+32)&0xffffffff;aligned=(case['length']+3)&0xfffffffc;empty_data=(empty_data-aligned)&0xffffffff
       if remain>((32+aligned)&0xffffffff):remain=(remain-32-aligned)&0xffffffff
       else:remain=0;expect_return=2;break
     put(expected,32,empty_idx);put(expected,36,empty_data);put(expected,28,remain)
   outputs=[]
   for side,u in enumerate(machines):
    data=bytearray(b'\x69'*512);put(data,0,DB+300);put(data,8,DB+400);put(data,12,256);put(data,88,99);data[25]=0;data[300:305]=b'logs\0';data[404:409]=b'path\0';u.mem_write(DB,bytes(data));u.mem_write(SP-512,bytes([case['fill']])*1024)
    for r,v in zip(REGS,[DB,256,0 if case['null'] else SEC,case['traversal']]):u.reg_write(r,v)
    for i,r in enumerate(SAVED):u.reg_write(r,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,header=bytes(header),trace=[],**{'assert':None});states[id(u)]=s;u.emu_start(0x87c25,0x20000100,count=10000)
    assert s['assert']==expect_assert,(case,s['assert'],expect_assert)
    if not expect_assert:
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(r) for r in SAVED]==[0x12340000+i for i in range(8)]
     assert u.reg_read(UC_ARM_REG_R0)==expect_return and bytes(u.mem_read(SEC,40))==expected,(case,u.reg_read(UC_ARM_REG_R0),expect_return,bytes(u.mem_read(SEC,40)).hex(),expected.hex())
    outputs.append([[u.reg_read(r) for r in REGS],u.reg_read(UC_ARM_REG_SP),s['assert'],s['trace'],bytes(u.mem_read(DB,512)).hex(),bytes(u.mem_read(SP-512,1024)).hex()])
   assert outputs[0]==outputs[1],case;counts['assertion_loop' if expect_assert else 'returned']+=1;digest.update(json.dumps([case,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,trace_sha256=digest.hexdigest(),object_sha256=sha(obj),log_object_sha256=sha(logobj),count_object_sha256=sha(countobj),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),partition_and_printf_are_fixtures=True,actual_log_flash_status_and_db_path_execute=True,all_0_through_80_header_prefix_lengths_checked=True,both_native_assertion_loops_observed=True,independent_sector_layout_space_and_return_oracle=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'direct-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

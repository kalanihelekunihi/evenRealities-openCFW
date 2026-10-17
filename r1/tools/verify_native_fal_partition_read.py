#!/usr/bin/env python3
"""FAL native/source wrapped bounds, callback returns, mutation and assertions."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-fal-partition-read';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;PART=0x20010000;BUF=PART+128;DEV=PART+256;READ=0x20001000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 obj=OUT/'native_fal_partition_read.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts={'returned':0,'assertion_loop':0,'device_read_calls':0,'negative_callback_returns':0};spans=[('read',0x631e8,368,'.text.r1_fdb_native_partition_read'),('name',0x9c48e,19,'.r1.fal.read_name'),('missing',0xc0b50,73,'.r1.fal.read_missing_device')]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS {'+''.join(' .%s 0x%x : { *(%s) }'%(n,a,l) for n,a,s,l in spans)+' /DISCARD/ : { *(.ARM.exidx*) } }\nr1_native_printf = 0x38061; r1_fal_native_device_by_partition = 0x64f75;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacement=[]
  for name,a,length,section in spans:
   p=td/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();assert len(d)==length and d==image[a-0x27000:a-0x27000+length];replacement.append((a,d))
  def put(u,p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   s=states[id(u)];c=s['case'];r=[u.reg_read(x) for x in REGS]
   if a in [0x63228,0x63234]:s['assert']=hex(a);u.emu_stop();return
   if a==0x38060:
    s['trace'].append(['log',r,bytes(u.mem_read(r[0],100)).split(b'\0')[0].decode()]);u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0xa1);u.reg_write(UC_ARM_REG_R2,0xa2);u.reg_write(UC_ARM_REG_R3,0xa3)
   elif a==0x64f74:
    assert r[0]==PART;s['trace'].append(['lookup',r]);u.reg_write(UC_ARM_REG_R0,DEV if c['device'] else 0)
    if c['mutation']:put(u,PART+52,c['new_offset']);put(u,PART+56,0)
   elif a==READ:
    expected=[((c['new_offset'] if c['mutation'] else c['offset'])+c['address'])&0xffffffff,c['buffer'],c['size']];assert r[:3]==expected,(c,r,expected);s['trace'].append(['read',r]);u.mem_write(r[1],bytes(range(min(c['size'],16))));u.reg_write(UC_ARM_REG_R0,c['result']);u.reg_write(UC_ARM_REG_R1,0x11111111);u.reg_write(UC_ARM_REG_R2,0x22222222);u.reg_write(UC_ARM_REG_R3,0x33333333)
   else:return
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacement:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  edge=[0,1,16,0x7fffffff,0x80000000,0xfffffffe,0xffffffff];cases=[]
  for i,(length,address,size,device,result,mutation) in enumerate(itertools.product(edge,edge,edge,range(2),[0,1,0x7fffffff,0x80000000,0xffffffff],range(2))):cases.append(dict(length=length,address=address,size=size,device=device,result=result,mutation=mutation,offset=edge[i%7],new_offset=edge[(i+2)%7],part=PART,buffer=BUF if i%2 else PART+52,fill=[0,0x96,255][i%3]))
  for part,buffer in [(0,BUF),(PART,0),(0,0)]:cases.append(dict(length=0,address=0,size=0,device=0,result=0,mutation=0,offset=0,new_offset=0,part=part,buffer=buffer,fill=0x96))
  for c in cases:
   outputs=[];expected_assert='0x63228' if not c['part'] else '0x63234' if not c['buffer'] else None;bound=((c['address']+c['size'])&0xffffffff)<=c['length'];called=not expected_assert and bound and c['device'];expected=(c['result'] if called else 0xffffffff)
   for side,u in enumerate(machines):
    u.mem_write(PART,b'\x69'*512);u.mem_write(PART+4,b'logs\0');u.mem_write(PART+28,b'flash\0');put(u,PART+52,c['offset']);put(u,PART+56,c['length']);put(u,DEV+40,READ+1);u.mem_write(SP-256,bytes([c['fill']])*512)
    for r,v in zip(REGS,[c['part'],c['address'],c['buffer'],c['size']]):u.reg_write(r,v)
    for i,r in enumerate(SAVED):u.reg_write(r,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=c,trace=[],**{'assert':None});states[id(u)]=s;u.emu_start(0x631e9,0x20000100,count=1000);assert s['assert']==expected_assert
    assert sum(x[0]=='lookup' for x in s['trace'])==int(not expected_assert and bound) and sum(x[0]=='read' for x in s['trace'])==int(bool(called))
    if not expected_assert:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(r) for r in SAVED]==[0x12340000+i for i in range(8)] and u.reg_read(UC_ARM_REG_R0)==expected,(c,u.reg_read(UC_ARM_REG_R0),expected)
    outputs.append([[u.reg_read(r) for r in REGS],u.reg_read(UC_ARM_REG_SP),s['assert'],s['trace'],bytes(u.mem_read(PART,512)).hex(),bytes(u.mem_read(SP-256,512)).hex()])
   assert outputs[0]==outputs[1],c;counts['assertion_loop' if expected_assert else 'returned']+=1;counts['device_read_calls']+=int(bool(called));counts['negative_callback_returns']+=int(bool(called) and c['result']&0x80000000!=0);digest.update(json.dumps([c,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=len(cases),counts=counts,trace_sha256=digest.hexdigest(),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),lookup_device_read_callback_and_printf_are_fixtures=True,wrapped_bounds_and_offset_fresh_reads_independently_checked=True,output_alias_to_partition_offset_tested=True,both_assertion_loops_observed=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'direct-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

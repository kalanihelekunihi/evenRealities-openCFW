#!/usr/bin/env python3
"""Actual CRC/native serialization and fresh port/size/name behavior; writes are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-nv-class-writer-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();NODE=0x20010001

def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'nv-class-writer-source.o';assert sha(obj)==b['writer_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_nv_class_writer_verification.ld';states={};digest=hashlib.sha256();count=obs=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','ring','sdk']:
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_kv_port']==0x20006974
  for n,a,z in [('ring',0x917fc,50),('sdk',0x91838,44)]:assert sections[n]==raw[a-0x27000:a-0x27000+z]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_stock_crc16_modbus'] if source else 0x5d87c):
    st['after_crc']=u.reg_read(UC_ARM_REG_LR)&~1;st['events'].append(['actual_crc',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
   if st['after_crc']==a:
    st['after_crc']=None;st['events'].append(['crc_return',u.reg_read(UC_ARM_REG_R0)])
    if st['mutation']==1:u.mem_write(NODE+18,b'\x03\x00');u.mem_write(0x20006974,struct.pack('<I',0x20000880))
    elif st['mutation']==2:u.mem_write(NODE+20,b'\x01\x00')
    elif st['mutation']==3:u.mem_write(NODE+24,b'\x5a')
   kind=({0x20000200:'mode',0x20000204:'ring',0x20000208:'sdk'} if source else {0x914ec:'mode',0x91638:'ring',0x799c8:'sdk'}).get(a)
   if a in [0x20000220,0x20000224]:kind='write'
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['status']
   if kind=='write':
    assert r[1]==NODE and r[3]==a+1;st['events'].append(['write',r,hashlib.sha256(bytes(u.mem_read(r[1],r[2]))).hexdigest()])
    if st['mutation']==4:u.mem_write(NODE+4,b'mutated\0');u.mem_write(NODE+18,b'\xff\xff');u.mem_write(NODE+22,b'\x34\x12')
   elif kind=='mode':ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;st['events'].append(['mode',ret])
   elif kind=='ring':assert r[:3]==[0x04400000,0x917fc,0x917fc] and r[3]==NODE+4;st['events'].append(['ring',r,bytes(u.mem_read(NODE+4,12)).hex()])
   else:assert r[:3]==[0x001c0001,0x91838,NODE+4];st['events'].append(['sdk',r[:3],bytes(u.mem_read(NODE+4,12)).hex()])
   u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000)
   for n,a in [('ring',0x917fc),('sdk',0x91838)]:u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000]];cases=[]
  for number,(index,flags,size,m) in enumerate(itertools.product([0,1,7,0x3fff,0x4000,0xffff,0xffffffff],[0,1,2,3,0xffff],[0,1,4,12,24,52,124,255,256],range(5))):cases.append((index,flags,size,m,[0,1,0xffffffff][number%3],modes[number%8]))
  for status,mode,m in itertools.product([0,1,0xffffffff],modes,range(5)):cases.append((7,3,52,m,status,mode))
  cases.append((0xffffffff,3,65535,0,0,[0]));saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(index,flags,size,m,status,mode) in enumerate(cases):
   results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(NODE,struct.pack('<I',0x12345678)+b'example\0\0\0\0\0'+struct.pack('<HHHH',1,flags,size,0));u.mem_write(NODE+24,bytes((i*17+number)&255 for i in range(size)));u.mem_write(0x20006974,struct.pack('<I',0x20000800));u.mem_write(0x20000814,struct.pack('<I',0x20000221));u.mem_write(0x20000894,struct.pack('<I',0x20000225));states[id(u)]=dict(source=source,events=[],after_crc=None,status=status,modes=mode,mi=0,mutation=m)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[NODE,index,0x55667788,0x99aabbcc]):u.reg_write(reg,v)
    u.emu_start((syms['r1_store_class_record_write'] if source else 0x91780)|1,0x20000100,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    assert u.reg_read(UC_ARM_REG_R0)==int(status==0);memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[index,flags,size,m,status,mode],results=results),indent=2)+'\n');raise AssertionError((number,index,flags,size,m,status,mode))
   count+=1;obs+=len(results[0][1]);digest.update(json.dumps([number,index,flags,size,m,status,mode,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=count,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_source_crc16=True,index14_mask_offset_and_flags_before_callback_checked=True,fresh_port_and_size_after_crc_checked=True,post_crc_mutations_are_explicit_fixtures=True,write_failure_does_not_restore_dirty_flag_checked=True,callback_fourth_word_is_loaded_target_checked=True,only_port_write_and_logging_are_fixtures=True,raw_r0_callee_sp_and_nonstack_ram_checked=True,no_native_candidate_execution=True,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),whole_flash_or_commit_graph_executed=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

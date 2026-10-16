#!/usr/bin/env python3
"""Actual cached copy and formatter; SVC/FICR are controlled memory fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-device-id-reader-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();FRAME=0x2003efe8

def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'device-id-reader-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_device_id_reader_verification.ld';states={};digest=hashlib.sha256();obs=0;counts={'cached':0,'svc':0,'random':0}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','format','cache_text','valid','pointer','length']:
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  assert syms['r1_device_id_cache_valid']==0x20006da4 and syms['r1_device_id_cache_pointer']==0x20006e38 and syms['r1_device_id_cache_length']==0x20006e3c
  for n,a in [('format',0x6abc8),('cache_text',0xc0648)]:assert sections[n]==raw[a-0x27000:a-0x27000+len(sections[n])]
  cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
  for n,a in [('valid',0x20006da4),('pointer',0x20006e38),('length',0x20006e3c)]:assert sections[n]==cold[a-0x200064a8:a-0x200064a8+len(sections[n])]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_advertising_controller_address_get'] if source else 0x6aba4):
    assert bytes(u.mem_read(a,2))==b'\x6d\xdf';ptr=u.reg_read(UC_ARM_REG_R0);assert ptr==FRAME+8;st['events'].append(['svc109',ptr,bytes(u.mem_read(ptr,7)).hex(),st['write'],st['status']]);u.mem_write(ptr,st['address'][:st['write']]);u.reg_write(UC_ARM_REG_R0,st['status']);u.reg_write(UC_ARM_REG_PC,(a+2)|1)
   if a==(syms['r1_native_snprintf'] if source else 0x38080):
    r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];extra=list(struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8)));assert r[1:3]==[25,0x6abc8];st['events'].append(['actual_format',r,extra])
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x30000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x10000000,0x1000);u.mem_map(0x20000000,0x40000)
   for n,a in [('format',0x6abc8),('cache_text',0xc0648)]:u.mem_write(a,sections[n])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[]
  for valid,length,seed,dest in itertools.product([1,2,255],range(256),[0,0xffffffff],[0x20002000,0x20002001]):cases.append(('cached',valid,length,seed,dest,0,0,0,0))
  for write,status,first,seed in itertools.product([0,1,4,7],[0,1,0xffffffff],[0,1,0xffffffff,0x80000000,0x12345678,0xaabbccdd],[0,0xffffffff,0x12345678,0xaabb0000]):cases.append(('svc',0,24,seed,0x20002001,write,status,first,first^0xfedcba98))
  for number in range(256):
   v=hashlib.sha256(str(number).encode()).digest();first,second,seed=struct.unpack('<III',v[:12]);cases.append(('random',0,24,seed,0x20002000,7,[0,0xffffffff][number%2],first,second))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,valid,length,seed,dest,write,status,first,second) in enumerate(cases):
   outputs=[];address=bytes([0x81,0x12,0x34,0x56,0x78,0x9a,0xbc]) if kind!='random' else hashlib.sha256(('addr'+str(number)).encode()).digest()[:7]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(0x20001001,bytes(range(256)));u.mem_write(0x20006da4,bytes([valid]));u.mem_write(0x20006e38,struct.pack('<I',0x20001001));u.mem_write(0x20006e3c,bytes([length]));u.mem_write(0x10000060,struct.pack('<II',first,second));states[id(u)]=dict(source=source,events=[],write=write,status=status,address=address)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[dest,0x11223344,0x55667788,seed]):u.reg_write(reg,v)
    u.emu_start((syms['r1_native_device_id_read_boundary'] if source else 0x6ab88)|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    mem=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));outputs.append([[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]],states[id(u)]['events'],hashlib.sha256(mem).hexdigest(),bytes(u.mem_read(dest,256)).hex()])
   if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,valid,length,seed,dest,write,status,first,second],outputs=outputs),indent=2)+'\n');raise AssertionError((number,kind))
   counts[kind]+=1;obs+=len(outputs[0][1]);digest.update(json.dumps([number,kind,valid,length,seed,dest,write,status,first,second,address.hex(),outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),actual_musl_copy_complete_formatter_and_existing_sdk_svc_wrapper=True,svc109_and_ficr_are_controlled_fixtures=True,all_cached_byte_lengths_checked_in_mapped_backing=True,partial_svc_writes_retain_saved_seed_words=True,raw_r0_r1_r2_r3_callee_sp_nonstack_ram_and_output_checked=True,no_native_candidate_execution=True,runtime_admission_changed=False,hardware_write_executed=False,hardware_identity_or_svc_success_proven=False,cache_capacity_or_overlap_safety_proven=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

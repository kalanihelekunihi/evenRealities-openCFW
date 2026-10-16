#!/usr/bin/env python3
"""ADC cache workflows with actual source registry and string comparison."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-vbat-cache';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rp=BASE/'native-vbat-cache-runtime/report.json';r=json.loads(rp.read_text());obj=rp.parent/'vbat-cache-source.o';assert sha(obj)==r['cache_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_vbat_cache_verification.ld';states={};digest=hashlib.sha256();count=0;finds=0;compares=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';name=d/'name.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True)
  for section,path in [('.text',binary),('.name',name)]:subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(path)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_vbat_adc_device']==0x200068a0 and syms['r1_stock_registry_head']==0x20007680 and name.read_bytes()==b'vbat_adc\0'
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_stock_registry_find'] if source else 0x85ce0):
    assert u.reg_read(UC_ARM_REG_R0)==0x91454;st['events'].append(['find',struct.unpack('<I',u.mem_read(0x20007680,4))[0]])
    if st['mode']==1:u.mem_write(0x200068a0,struct.pack('<I',0xfedcba98))
    elif st['mode']==2:u.mem_write(0x20007680,struct.pack('<I',0x20003000))
   if a==(syms['strcmp'] if source else 0x277fe):
    left=u.reg_read(UC_ARM_REG_R0);right=u.reg_read(UC_ARM_REG_R1);assert right==0x91454;st['events'].append(['compare',left,right])
    if st['mode']==3:u.mem_write(0x200068a0,struct.pack('<I',0xabcdef01))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for length,match,cached,mode,reseed in itertools.product(range(7),range(8),[0,1,0x20003000,0xffffffff],range(4),[False,True]):
   results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000)
    for i in range(7):
     record=0x20003000+i*32;label=0x20004000+i*32;value=b'vbat_adc\0' if i==match else [b'\0',b'vbat_ad\0',b'vbat_adcX\0',b'VBAT_ADC\0',b'vbat_adb\0',b'vbat_add\0',b'other\0'][i];u.mem_write(label,value);u.mem_write(record,struct.pack('<6I',label,0,0,0,0,record+32 if i+1<length else 0))
    u.mem_write(0x200068a0,struct.pack('<I',cached));u.mem_write(0x20007680,struct.pack('<I',0x20003000 if length else 0));states[id(u)]=dict(source=source,mode=mode,events=[]);returns=[]
    for step in range(3):
     if step==1:
      u.mem_write(0x20007680,struct.pack('<I',0))
      if reseed:u.mem_write(0x200068a0,bytes(4))
     if step==2:u.mem_write(0x20007680,struct.pack('<I',0x20003000 if length else 0));u.mem_write(0x200068a0,bytes(4))
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     for reg,val in [(UC_ARM_REG_R0,0x1234),(UC_ARM_REG_R1,0x55667788),(UC_ARM_REG_R2,0x98765432),(UC_ARM_REG_R3,0xffffffff)]:u.reg_write(reg,val)
     u.emu_start((syms['r1_vbat_adc_handle_cache'] if source else 0x9143c)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];returns.append(u.reg_read(UC_ARM_REG_R0))
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([returns,states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   assert results[0]==results[1],(length,match,cached,mode,reseed,results)
   count+=1;finds+=sum(x[0]=='find' for x in results[0][1]);compares+=sum(x[0]=='compare' for x in results[0][1]);digest.update(json.dumps([length,match,cached,mode,reseed,results[0]],sort_keys=True).encode())
 receipt=dict(workflows=count,calls_per_workflow=3,find_calls_per_side=finds,strcmp_calls_per_side=compares,trace_sha256=digest.hexdigest(),actual_source_registry_and_strcmp=True,controlled_mutations_are_fixtures=True,full_observed_nonstack_ram_raw_r0_callee_and_sp_checked=True,no_native_candidate_body_execution=True,driver_sha256=sha(Path(__file__)),object_sha256=sha(obj),runtime_report_sha256=sha(rp),layout_sha256=sha(layout),application_sha256=sha(app),instruction_identity=False,physical_adc_verified=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

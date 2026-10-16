#!/usr/bin/env python3
"""Native eight-byte cached calendar output with real timestamp thunk and C runtime."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();STATE=0x20016ac4;REG=0x20006820;OUT=0x20003008

def main():
 out=BASE/'native-log-calendar';rp=out/'report.json';r=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True);objects=[];reports={}
 for name,file,key in [('native-log-calendar','log-calendar.o','selected_object_sha256'),('structured-time','structured_time.o',None),('integer-runtime','integer-runtime.o','relocatable_sha256'),('runtime','memory-runtime.o','relocatable_sha256')]:
  p=BASE/name/'report.json';q=json.loads(p.read_text());o=p.parent/file;assert sha(o)==(q[key] if key else q['units'][0]['object_sha256']);objects.append(o);reports[name+'/report.json']=sha(p)
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;callbacks=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.time.state 0x20016ac4 (NOLOAD) : { *(.r1.time.state) } .r1.time.registration 0x20006820 (NOLOAD) : { *(.r1.time.registration) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=r1_log_local_datetime_fill',*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_time_state']==STATE and syms['r1_time_registration']==REG
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for a,z in [(STATE,32),(REG,20)]:assert bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
  def hook(u,a,size,user):
   nonlocal callbacks
   if a!=0x100ed00:return
   f=states[id(u)];assert u.reg_read(UC_ARM_REG_R0)==0;f['trace'].append(('timestamp',f['epoch']));callbacks+=1
   if f['mutation'] is not None:u.mem_write(STATE+8,struct.pack('<h',f['mutation']))
   u.reg_write(UC_ARM_REG_R0,f['epoch']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def compare(epochs,offset=0,registered=1,cache=0,hit=False,null=False,mutation=None):
   nonlocal comparisons
   local=epochs[0]+offset*60;q=(abs(local)//86400)*(-1 if local<0 else 1);day=(q*86400-offset*60)&0xffffffff;initial=bytearray([0xa7]*32);struct.pack_into('<hBB',initial,8,offset,registered,0xb8);struct.pack_into('<I',initial,16,day if hit else 0xffffffff);initial[28]=cache;results=[]
   for u in (stock,candidate):
    states[id(u)]={'epoch':0,'mutation':mutation,'trace':[]};u.mem_write(STATE,bytes(initial));u.mem_write(REG,bytes(20));u.mem_write(REG+8,struct.pack('<I',0x20002000));u.mem_write(0x20002000,struct.pack('<5I',0,0,0x100ed01,0,0));u.mem_write(OUT-8,bytes([0x96])*32);steps=[]
    for epoch in epochs:
     states[id(u)]['epoch']=epoch;u.reg_write(UC_ARM_REG_R0,0 if null else OUT);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((0x8ac28 if u is stock else syms['r1_log_local_datetime_fill'])|1,0x20000100,count=1000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(epoch,offset);steps.append((bytes(u.mem_read(STATE,32)),bytes(u.mem_read(REG,20)),bytes(u.mem_read(OUT-8,32))))
    results.append((steps,states[id(u)]['trace']))
   assert results[0]==results[1],(epochs,offset,registered,cache,hit,null,mutation,results);comparisons+=1
  epochs=(0,1,86399,86400,951782400,1700000000,0x7fffffff,0x80000000,0xffffffff)
  for epoch,offset,reg,cache,hit,null in itertools.product(epochs,(-32768,-1440,-720,-1,0,1,840,32767),(0,1),(0,1),(False,True),(False,True)):compare([epoch],offset,reg,cache,hit,null)
  rng=random.Random(0x8ac28)
  for i in range(1024):
   epoch=rng.getrandbits(32);compare([epoch,(epoch+1)&0xffffffff,(epoch+86400)&0xffffffff],rng.randint(-32768,32767),registered=rng.choice((1,127,255)),cache=rng.choice((0,1,255)),hit=bool(i&1))
  for epoch,offset,mutation in itertools.product(epochs,(-720,0,840),(-32768,1,32767)):compare([epoch],offset,mutation=mutation)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,comparisons=comparisons,timestamp_callbacks_per_implementation=callbacks//2,source_shared_cold_zero_bytes=52,output_bytes=8,scope='Native cached date/time ABI with actual timestamp thunk, recovered Gregorian conversion, compiled signed64 division/copy; signed timezone edges, cache hits/misses, rollover, null/unregistered behavior and callback offset mutation',limitations=['Timestamp backend getter remains a fixture; no real RTC/clock registration or full logging-pipeline proof.','Only bounded aligned/nonoverlapping outputs and valid registered backend descriptors are tested.','The recovered converter is called through its contextual C ABI internally; native standalone converter ABI is not independently admitted here. Whole-image linking, physical behavior and byte identity remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'calendar comparisons;',callbacks//2,'timestamp callbacks')
if __name__=='__main__':main()

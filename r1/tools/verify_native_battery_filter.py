#!/usr/bin/env python3
"""Authenticate and compare product five-sample filter, including partial/no writes."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-filter';CTX=0x20006890
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PROVIDERS={'r1_stock_dispatch_08':0x85d1a,'r1_stock_dispatch_0c':0x85cba,'r1_stock_dispatch_10':0x85d2c,'nrf_delay_ms':0x78550,'osDelay':0x7d154}
def main():
 receipt=OUT/'verification.json';receipt.unlink(missing_ok=True);report=OUT/'report.json';r=json.loads(report.read_text());obj=OUT/'native_battery_filter.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={}
 for filename in ('rea-next-91184-body.json','rea-next-91184-pseudocode.json','ghidra-next-91184.json','next-91184-assembly.txt'):
  data=(BASE/'native-battery-runtime'/filename).read_bytes();p=OUT/filename;p.write_bytes(data);evidence[filename]=sha(p)
 q=json.loads((OUT/'rea-next-91184-body.json').read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==182 and q['normalized_result']['entrypoint']=='0x91184'
 assert bytes(json.loads((OUT/'ghidra-next-91184.json').read_text())['data'])==app.read_bytes()[0x91184-0x27000:0x91184-0x27000+192]
 rng=random.Random(0x91184);patterns=[(0,)*5,(65535,)*5,(1,2,3,4,5),(5,4,3,2,1),(0,0,65535,65535,65535),(7,7,7,7,7),(65535,1,65535,1,65535)]
 patterns += [(n,)*5 for n in (1,2,3,255,256,1023,4095,8191,16383,32767,32768,49151,65534)]
 patterns += [tuple(rng.randrange(65536) for _ in range(5)) for _ in range(128)]
 counts={'comparisons':0,'adc_reads':0,'busy_delays':0,'rtos_delays':0};states={};machines=[]
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(PROVIDERS)}
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_battery_runtime_context='+hex(CTX),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True)
  subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in PROVIDERS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,address,size,_):
   if address not in kinds:
    if u is machines[1] and address<0x1000000 and address!=0x20000100:raise AssertionError(('source executed native',hex(address)))
    return
   f=states[id(u)];name=kinds[address];a=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];handle=struct.unpack('<I',bytes(u.mem_read(CTX+16,4)))[0]
   if name in ('r1_stock_dispatch_08','r1_stock_dispatch_0c'):assert a[0]==handle;event=(name,handle)
   elif name=='r1_stock_dispatch_10':
    assert a[0]==handle and a[1]==0 and a[3]==1
    before=struct.unpack('<I',bytes(u.mem_read(a[2],4)))[0];assert before==f['word'],(hex(before),hex(f['word']))
    i=f['reads'];value=(0xa5000000+(i<<16))|f['samples'][i];width=(0,1,2,4)[(f['width']+i)%4] if f['width']==4 else f['width']
    if width:u.mem_write(a[2],struct.pack('<I',value)[:width])
    after=struct.unpack('<I',bytes(u.mem_read(a[2],4)))[0];f['actual'].append(after&65535);f['word']=after&0xffff0000;f['reads']+=1;event=(name,handle,before,after,width)
   else:
    mode=bytes(u.mem_read(CTX+1,1))[0];assert a[0]==2 and name==('osDelay' if mode else 'nrf_delay_ms');event=(name,2);f['delays'][name]+=1
   f['trace'].append(event)
   if f['mutate']:
    index=len(f['trace']);u.mem_write(CTX+16,struct.pack('<I',0x20010000+index*16));u.mem_write(CTX+1,bytes([(0,1,255)[index%3]]))
   for reg,value in [(UC_ARM_REG_R0,0x80000007),(UC_ARM_REG_R1,0x87654321),(UC_ARM_REG_R2,0x76543210),(UC_ARM_REG_R3,0xdeadbeef)]:u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for samples,width,seed,mode,mutate in itertools.product(patterns,(0,1,2,4),(0,0x1234abcd,0xffffffff),(0,1),(False,True)):
   results=[]
   for candidate,u in enumerate(machines):
    f={'trace':[],'word':seed&0xffff0000,'samples':samples,'width':width,'reads':0,'actual':[],'mutate':mutate,'delays':{'nrf_delay_ms':0,'osDelay':0}};states[id(u)]=f;u.mem_write(CTX,bytes(32));u.mem_write(CTX+1,bytes([mode]));u.mem_write(CTX+16,struct.pack('<I',0x20010000));u.mem_write(0x2003ef00,b'\x96'*256)
    for reg,value in [(UC_ARM_REG_R0,seed),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_battery_five_sample_filter_and_conversion'] if candidate else 0x91184)|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    kept=sorted(f['actual'])[2:];average=(sum(kept)//3)&65535;expected=(((average*292*2989)&0xffffffff)//0x79d38)&65535
    assert u.reg_read(UC_ARM_REG_R0)==expected,(samples,width,seed,mode,mutate,u.reg_read(UC_ARM_REG_R0),expected)
    assert f['reads']==5 and sum(f['delays'].values())==5
    results.append((expected,f['trace'],bytes(u.mem_read(CTX,32))))
   assert results[0]==results[1];counts['comparisons']+=1;counts['adc_reads']+=5;counts['busy_delays']+=f['delays']['nrf_delay_ms'];counts['rtos_delays']+=f['delays']['osDelay']
 receipt.write_text(json.dumps(dict(**counts,sample_patterns=len(patterns),incoming_seeds=3,write_widths=[0,1,2,4],live_context_mutation=True,report_sha256=sha(report),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Registry and delay endpoints modeled; actual ADC/Nordic/RTOS composition remains open','Incoming r0 high-half captured explicitly; selected compiler boundary verified, other compilers/LTO require revalidation','Runtime context ownership, full startup, physical sampling and original image identity remain open']),indent=2)+'\n');print('Native battery filter:',counts)
if __name__=='__main__':main()

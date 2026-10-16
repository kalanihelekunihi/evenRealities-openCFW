#!/usr/bin/env python3
"""Native hardware TWI constructors, cold records and real registry semantics."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();START=0x20006fe8
ENTRIES={'r1_twi_primary_device_binding_configuration':0x54f90,'r1_twi_secondary_device_binding_configuration':0x54fc4}
POINTERS=[(44,'r1_hw_twi0_irq',0x70778),(80,'r1_hw_twi0_open',0x55278),(84,'r1_hw_twi0_close',0x55180),(88,'r1_hw_twi0_read',0x55414),(92,'r1_hw_twi0_write',0x55ce0),(152,'r1_hw_twi1_irq',0x707cc),(188,'r1_hw_twi1_open',0x552e4),(192,'r1_hw_twi1_close',0x551b4),(196,'r1_hw_twi1_read',0x55448),(200,'r1_hw_twi1_write',0x55d50)]
def main():
 out=BASE/'native-hw-twi-registration';rp=out/'report.json';r=json.loads(rp.read_text());objects=[out/'hw-twi-registration.o',BASE/'i2c5/stock_registry.o',BASE/'runtime/memory-runtime.o'];reports={n+'/report.json':sha(BASE/n/'report.json') for n in ('native-hw-twi-registration','i2c5','runtime')};assert sha(objects[0])==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0;sem_calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.hw_twi.primary 0x20006fe8 : { *(.r1.hw_twi.primary) } .r1.hw_twi.secondary 0x20007054 : { *(.r1.hw_twi.secondary) } .r1.hw_twi.name0 0xc06e4 : { *(.r1.hw_twi.name0) } .r1.hw_twi.name1 0xc06ec : { *(.r1.hw_twi.name1) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ed01+i*16 for i,(_,n,_) in enumerate(POINTERS)};bindings['osSemaphoreNew']=0x100ef01;subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for section,a,z in [('.r1.hw_twi.primary',START,108),('.r1.hw_twi.secondary',START+108,108),('.r1.hw_twi.name0',0xc06e4,6),('.r1.hw_twi.name1',0xc06ec,6)]:
   p=t/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);data=p.read_bytes();assert len(data)==z;candidate.mem_write(a,data)
  def normalized(u):
   data=bytearray(u.mem_read(START,216))
   for off,name,a in POINTERS:
    assert struct.unpack_from('<I',data,off)[0]==(a|1 if u is stock else bindings[name]);struct.pack_into('<I',data,off,a|1)
   return bytes(data)
  assert normalized(stock)==normalized(candidate)
  for a in (0xc06e4,0xc06ec):assert bytes(stock.mem_read(a,6))==bytes(candidate.mem_read(a,6))
  initial={id(u):bytes(u.mem_read(START,216)) for u in (stock,candidate)};handle=0
  def hook(u,a,size,user):
   nonlocal sem_calls
   if a not in (0x7d60c,0x100ef00):return
   args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];assert args==[1,0,0];states[id(u)].append(('semaphore',args,struct.unpack('<I',bytes(u.mem_read(0x20007680,4)))[0]));sem_calls+=1;u.reg_write(UC_ARM_REG_R0,handle);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,flag,handle,head_kind,opened,old_handle in itertools.product(ENTRIES,(0,1,255),(0,1,0x20003800,0xffffffff),range(3),(0,1,255),(0,0x12345678)):
   index=0 if name.startswith('r1_twi_primary') else 1;cluster=START+index*108;device=cluster+48;flag_address=cluster+(2 if index==0 else 1)
   for u in (stock,candidate):
    u.mem_write(START,initial[id(u)]);u.mem_write(START-16,bytes([0x6d])*16);u.mem_write(START+216,bytes([0x6d])*16);u.mem_write(flag_address,bytes([flag]));u.mem_write(cluster+4,struct.pack('<I',old_handle));u.mem_write(cluster+16,bytes([opened]));u.mem_write(device+20,struct.pack('<I',0x87654321));u.mem_write(0x20007680,struct.pack('<I',0x20002000 if head_kind else 0));u.mem_write(0x20003000,b'other\0');u.mem_write(0x20002000,struct.pack('<6I',0xc06e4+index*8 if head_kind==1 else 0x20003000,1,0,0,0,0))
   for repeat in range(2):
    results=[]
    for u in (stock,candidate):
     states[id(u)]=[];u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)],normalized(u),bytes(u.mem_read(0x20007680,4)),bytes(u.mem_read(0x20002000,24)),bytes(u.mem_read(START-16,16)),bytes(u.mem_read(START+216,16))))
    assert results[0]==results[1],(name,flag,handle,head_kind,opened,old_handle,repeat,results);assert results[0][0]==bool(handle);count+=1;handle=0 if handle else 0x20003800
 (out/'verification.json').write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,provider_objects={str(p.relative_to(BASE)):sha(p) for p in objects},comparisons=count,semaphore_calls_per_implementation=sem_calls//2,cold_configuration_bytes_pointer_normalized=216,name_bytes=12,scope='Actual native/source hardware TWI constructors and registry/memory; cold metadata, duplicate/append/empty registration, repeated semaphore creation, stale flags and failure transitions; semaphore allocator fixture',limitations=['Ten operation/IRQ targets are metadata-only bindings; their bodies/ABIs and actual semaphore allocator remain unresolved. No hardware I2C behavior, IRQ completion or full initcall execution is proven.']),indent=2)+'\n');print(count,'hardware TWI registration comparisons;',sem_calls//2,'semaphore calls')
if __name__=='__main__':main()

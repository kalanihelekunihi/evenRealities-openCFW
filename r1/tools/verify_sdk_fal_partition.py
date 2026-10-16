#!/usr/bin/env python3
"""Pinned FAL partition init/find/cache validation against locked stock."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIELDS={'r1_fal_partition_initialized':(0x200077b4,1),'r1_fal_partition_table':(0x200077b8,4),'r1_fal_partition_count':(0x200077bc,4),'r1_fal_partition_cache':(0x2001e544,28)}
TABLE=0x9c250;CUSTOM=0x20002000;DEVICE=0x20001000;QUERY=0x20003000
ENTRIES={'fal_partition_init':0x631c0,'fal_partition_find':0x63150,'check_and_update_part_cache':0x57e1c}
def main():
 out=BASE/'sdk-fal-partition';rp=out/'report.json';obj=out/'fal-partition.o';r=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 mr=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(mr.read_text())['relocatable_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};count=0;assertions=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in FIELDS.items())+'.rodata.r1_fal_partition_records 0x9c250 : { *(.rodata.r1_fal_partition_records) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=fal_partition_init','--defsym=fal_flash_device_find=0x100e001','--defsym=printf=0x100e021',str(obj),str(memory),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  for n,(a,z) in FIELDS.items():assert syms[n]==a
  p=t/'table.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.rodata.r1_fal_partition_records='+str(p),str(elf)],check=True);table=p.read_bytes();assert len(table)==448
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());candidate.mem_write(TABLE,table);assert bytes(stock.mem_read(TABLE,448))==table
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for a,z in FIELDS.values():assert bytes(stock.mem_read(a,z))==bytes(z)
  def string(u,a):
   b=bytearray()
   while True:
    x=bytes(u.mem_read(a+len(b),1))
    if x==b'\0':return b.decode()
    b+=x;assert len(b)<256
  def hook(u,address,size,user):
   f=states[id(u)]
   if f['asserted']:
    if address==f['last_pc']:f['repeats']+=1
    else:f['last_pc']=address;f['repeats']=0
    if f['repeats']==8:u.emu_stop();return
   if address in (0x62df4,0x100e000):
    i=f['lookups'];f['lookups']+=1;f['trace'].append(('find_device',string(u,u.reg_read(UC_ARM_REG_R0))));result=DEVICE if f['mask']&(1<<(i%7)) else 0
    if f['mutation']:u.mem_write(0x200077bc,struct.pack('<I',f['mutation']))
   elif address in (0x38060,0x100e020):
    fmt=string(u,u.reg_read(UC_ARM_REG_R0));a=[u.reg_read(reg) for reg in (UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if 'assert failed' in fmt:args=[string(u,a[0]),string(u,a[1])];f['asserted']=True
    elif '%s:%d' in fmt:args=[string(u,a[0]),a[1]]
    elif 'Partition(%s)' in fmt:args=[string(u,a[0]),a[1],a[2]]
    else:args=[]
    f['trace'].append(('printf',fmt,args));result=f['printf_result']
   else:return
   u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,name,initial=0,preset_count=7,mask=127,length=0x24000,offset=None,items=7,query=b'kv.bin\0',mutation=0,printf_result=0):
   u.mem_write(0x200077b4,bytes([initial,0x73,0x91,0x83])+struct.pack('<II',CUSTOM,preset_count));u.mem_write(0x2001e540,b'LEFT'+bytes([0xa7])*28+b'RGHT');records=bytearray(table)
   if offset is not None:
    for i in range(7):struct.pack_into('<I',records,i*64+52,offset)
   u.mem_write(CUSTOM,bytes(records));u.mem_write(QUERY,query.ljust(64,b'\x7f'));u.mem_write(DEVICE,bytes(28)+struct.pack('<I',length));f=dict(trace=[],asserted=False,last_pc=0,repeats=0,lookups=0,mask=mask,mutation=mutation,printf_result=printf_result);states[id(u)]=f
   u.reg_write(UC_ARM_REG_R0,CUSTOM if name=='check_and_update_part_cache' else QUERY);u.reg_write(UC_ARM_REG_R1,items);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=10000)
   if f['asserted']:assert f['repeats']==8 and u.reg_read(UC_ARM_REG_PC)!=0x20000100
   else:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   assert bytes(u.mem_read(0x2001e540,4))==b'LEFT' and bytes(u.mem_read(0x2001e560,4))==b'RGHT'
   return None if f['asserted'] else u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200077b4,12)),bytes(u.mem_read(0x2001e544,28)),f['trace'],f['asserted']
  def compare(name,**kw):
   nonlocal count,assertions
   a=run(stock,name,**kw);b=run(candidate,name,**kw);assert a==b,(name,kw,a,b);count+=1;assertions+=a[-1]
  for initial,preset_count in itertools.product(range(256),(0,1,7,0xffffffff)):compare('fal_partition_init',initial=initial,preset_count=preset_count)
  for mask,length in itertools.product(range(128),(0,1,8192,98304,98305,0x24000,0x7fffffff,0x80000000,0xffffffff)):compare('fal_partition_init',mask=mask,length=length)
  for items,offset,length in itertools.product(range(8),(0,1,0x7fffffff,0x80000000,0xffffffff),(0,1,0x7fffffff,0x80000000,0xffffffff)):compare('check_and_update_part_cache',items=items,offset=offset,length=length)
  for mask,mutation,result in itertools.product(range(128),(0,1,8),(0,8,0xffffffff)):compare('check_and_update_part_cache',mask=mask,mutation=mutation,printf_result=result)
  for initial in range(256):compare('fal_partition_find',initial=initial)
  for i in range(7):
   q=table[i*64+4:i*64+28].split(b'\0')[0]+b'\0';compare('fal_partition_find',initial=1,query=q)
   for n in range(len(q)):
    for value in range(256):
     b=bytearray(q);b[n]=value;compare('fal_partition_find',initial=1,query=bytes(b))
  for n in range(8):compare('fal_partition_find',initial=1,preset_count=n,query=b'log.bin\0')
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),memory_report_sha256=sha(mr),comparisons=count,terminal_assertion_comparisons=assertions,cold_zero_bytes_compared=sum(z for a,z in FIELDS.values()),partition_record_bytes_compared=448,scope='Pinned partition init/find/cache: seven exact records, all readiness bytes, all missing-device masks, signed offset/device-length boundaries, partial cache effects and count mutation, native error printf, lookup strings and terminal assertion, guards/registers',limitations=['Device lookup and printf are controlled callbacks; real FAL device/driver and runtime output remain gates.','Only mapped bounded tables/names are covered; invalid/null strcmp pointers and cache overflow are not portable contracts.','Instruction identity, whole image and hardware remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(count,'FAL partition comparisons passed;',assertions,'terminal assertions')
if __name__=='__main__':main()

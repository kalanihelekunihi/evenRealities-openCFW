#!/usr/bin/env python3
"""Native KV initialization differential with explicit FAL/CMSIS/scan fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
STRINGS={'mutex_name':0xc01d8,'partition_name':0x94f98,'part_ring':0x94fa8,'part_sdk':0x94fd0,'driver_ring':0x94ff0,'driver_sdk':0x9501c,'size_ring':0x95040,'size_sdk':0x95074,'ready_ring':0x950a4,'ready_sdk':0x950e0}
FIELDS={'storage_context':(0x2000697c,4),'storage_driver':(0x20006980,4),'block_count':(0x20019e48,1),'erase_threshold':(0x20019e4a,1),'block_stride':(0x20019e4c,4),'partition_size':(0x20019e50,4),'mutex_storage':(0x20019e54,80)}
CALLS={'osMutexNew':0x7d4d6,'r1_fal_is_initialized':0x62fe8,'fal_init':0x62f40,'fal_partition_find':0x63150,'fal_flash_device_find':0x62df4,'r1_kv_flash_erase_scan':0x57d0c,'r1_latest_valid_flash_slot_scan_adapter':0x64b24,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0,'nrf_log_frontend_std_2':0x799d6,'nrf_log_frontend_std_4':0x799f8}
I=0x20001000;D=0x20001200

def main():
 real_scans='--real-scans' in sys.argv
 out=BASE/'native-kv-initialize';rp=out/'report.json';obj=out/'native_kv_initialize.o';report=json.loads(rp.read_text());receipt=out/('scan-integration-verification.json' if real_scans else 'verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==report['units'][0]['object_sha256']
 for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 states={};count=0
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'test.ld';elf=tmp/'test.elf';binary=tmp/'text.bin'
  from verify_native_kv_scans import STRINGS as SCAN_STRINGS
  scan_obj=BASE/'native-kv-scans/native_kv_scans.o';scan_rp=BASE/'native-kv-scans/report.json';memory=BASE/'runtime/memory-runtime.o';memory_rp=BASE/'runtime/report.json'
  if real_scans:assert sha(scan_obj)==json.loads(scan_rp.read_text())['units'][0]['object_sha256'] and sha(memory)==json.loads(memory_rp.read_text())['relocatable_sha256']
  scan_sections=''.join('.r1.kv.scan.log.'+n+' '+hex(a)+' : { *(.r1.kv.scan.log.'+n+') } ' for n,a in SCAN_STRINGS.items()) if real_scans else ''
  ld.write_text('SECTIONS { '+scan_sections+''.join('.r1.kv.init.log.'+n+' '+hex(a)+' : { *(.r1.kv.init.log.'+n+') } ' for n,a in STRINGS.items())+''.join('.r1.kv.'+n+' '+hex(a)+' (NOLOAD) : { *(.r1.kv.'+n+') } ' for n,(a,z) in FIELDS.items())+'.r1.kv.mutex_attributes 0x9a0e8 : { *(.r1.kv.mutex_attributes) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  defs={n:0x100e001+i*16 for i,n in enumerate(CALLS) if not (real_scans and n in ('r1_kv_flash_erase_scan','r1_latest_valid_flash_slot_scan_adapter'))};defs.update(r1_kv_mutex=0x20006978,r1_kv_block_cursor=0x20019e49)
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_kv_port_initialize',*['--defsym='+n+'='+hex(a) for n,a in defs.items()],str(obj),*([str(scan_obj),str(memory)] if real_scans else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for n,(a,z) in FIELDS.items():assert bytes(stock.mem_read(a,z))==bytes(z)
  descriptor_bytes=0
  for section,a in ([('.r1.kv.scan.log.'+n,a) for n,a in SCAN_STRINGS.items()] if real_scans else [])+[('.r1.kv.init.log.'+n,a) for n,a in STRINGS.items()]+[('.r1.kv.mutex_attributes',0x9a0e8)]:
   p=tmp/(str(a)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);b=p.read_bytes();assert bytes(stock.mem_read(a,len(b)))==b;candidate.mem_write(a,b);descriptor_bytes+=len(b)
  names={a:n for n,a in CALLS.items()};names.update({(syms[n] if real_scans and n in ('r1_kv_flash_erase_scan','r1_latest_valid_flash_slot_scan_adapter') else defs[n]&~1):n for n in CALLS})
  def hook(uc,address,size,user):
   if real_scans and address in (0x100f400,0x100f410):
    f=states[id(uc)];a=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];f['trace'].append(('driver_read' if address==0x100f400 else 'driver_erase',a[0],a[2] if address==0x100f400 else a[1]))
    if address==0x100f400:
     assert a[2]==24;magic=0 if f['scan']%3==0 else 0x87654321 if f['scan']%3==1 else 0xffffffff;uc.mem_write(a[1],struct.pack('<6I',0,0,0,magic,0,0))
     if f['mutation']&1:uc.mem_write(0x2000697c,struct.pack('<I',I+0x100))
     if f['mutation']&2:uc.mem_write(0x20019e4a,b'\x19')
    uc.reg_write(UC_ARM_REG_R0,24 if address==0x100f400 else 0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   if address not in names:return
   n=names[address];f=states[id(uc)];a=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];result=0
   if n=='r1_structured_log_mode_get':result=f['modes'][f['mode_calls']%len(f['modes'])];f['mode_calls']+=1
   elif n=='r1_structured_log_format':
    argc={0x04000000:0,0x04800000:2,0x0d000000:4,0x0c800000:2,0x0c000000:0}[a[0]];vals=a[:3]+(a[3:] if argc else [])
    if argc>1:vals+=list(struct.unpack('<'+'I'*(argc-1),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4*(argc-1)))))
    f['trace'].append((n,vals))
   elif n.startswith('nrf_log_frontend_std_'):
    argc=int(n[-1]);vals=a[:min(4,2+argc)]
    if argc>2:vals+=list(struct.unpack('<'+'I'*(argc-2),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4*(argc-2)))))
    f['trace'].append((n,vals))
   else:
    if real_scans and n in ('r1_kv_flash_erase_scan','r1_latest_valid_flash_slot_scan_adapter'):
     f['trace'].append((n,bytes(uc.mem_read(0x20006978,12)),bytes(uc.mem_read(0x20019e48,12))));return
    if n=='osMutexNew':assert a[0]==0x9a0e8;result=f['mutex_result']
    elif n=='r1_fal_is_initialized':result=f['ready']
    elif n=='fal_init':result=0xffffffff
    elif n=='fal_partition_find':assert a[0]==0x94f98;result=I if f['partition'] else 0
    elif n=='fal_flash_device_find':assert a[0]==I+28;result=D if f['driver'] else 0
    elif n=='r1_kv_flash_erase_scan':
     if f['mutation']&1:uc.mem_write(0x2000697c,struct.pack('<I',I+0x100))
     if f['mutation']&2:uc.mem_write(0x20019e4a,b'\x19')
    elif n=='r1_latest_valid_flash_slot_scan_adapter':result=f['scan']
    f['trace'].append((n,bytes(uc.mem_read(0x20006978,12)),bytes(uc.mem_read(0x20019e48,12))))
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(uc,mutex=0,mutex_result=0x20000700,ready=1,partition=True,driver=True,length=8192,scan=2,mutation=0,modes=(0,)):
   uc.mem_write(0x20006978,struct.pack('<III',mutex,I+0x100,D+0x100));uc.mem_write(0x20019e48,bytes(range(12)))
   for i in range(2):uc.mem_write(I+i*0x100,bytes(28)+b'nrf52_onchip_flash'.ljust(24,b'\0')+struct.pack('<II',0xd4000+i*4096,(length+i*2048)&0xffffffff))
   if real_scans:uc.mem_write(D,bytes(40)+struct.pack('<III',0x100f401,0,0x100f411))
   f=dict(trace=[],mode_calls=0,modes=modes,mutex_result=mutex_result,ready=ready,partition=partition,driver=driver,scan=scan,mutation=mutation);states[id(uc)]=f
   uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
   uc.emu_start((0x94e3c if uc is stock else syms['r1_kv_port_initialize'])|1,0x20000100,count=1000000 if real_scans else 10000)
   assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
   return uc.reg_read(UC_ARM_REG_R0),f['trace'],f['mode_calls'],bytes(uc.mem_read(0x20006978,12)),bytes(uc.mem_read(0x20019e48,12))
  def compare(**kw):
   nonlocal count
   a=run(stock,**kw);b=run(candidate,**kw);assert a==b,(kw,a,b);count+=1
  for mutex,mutex_result,ready,partition,driver,length in itertools.product((0,0x20000700),(0,0x20000700),(0,1,0xffffffff),(False,True),(False,True),(0,2047,2048,8192)):compare(mutex=mutex,mutex_result=mutex_result,ready=ready,partition=partition,driver=driver,length=length)
  for length in ([2047,2048,4096,8192,524288] if real_scans else list(range(2040,2057))+[4095,4096,8191,8192,524287,524288,1048576,0x7fffffff,0xffffffff]):
   for scan,mutation,mode in itertools.product((0,1,255,256,0xffffffff),range(4),range(8)):compare(length=length,scan=scan,mutation=mutation,modes=(mode,))
  for mode in range(256):
   for kw in ({'partition':False},{'driver':False},{'length':2047},{'length':8192}):compare(modes=(mode,),**kw)
  for modes in itertools.product(range(8),repeat=3):
   for kw in ({'partition':False},{'driver':False},{'length':2047},{}):compare(modes=modes,**kw)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),comparisons=count,actual_native_scans_executed=real_scans,scan_report_sha256=sha(scan_rp) if real_scans else None,memory_report_sha256=sha(memory_rp) if real_scans else None,initial_zero_bytes_compared=sum(z for a,z in FIELDS.values()),descriptor_bytes_compared=descriptor_bytes,scope='Native initializer error precedence, cached mutex/null allocation, FAL readiness, partition/device outcomes, minimum length and byte truncation geometry, scan mutation, cursor truncation, descriptors and log mode/arguments, state and callee-saved registers',limitations=['FAL/CMSIS and driver callbacks are controlled providers; scans are actual native C only in scan integration mode. No physical allocation, persistence or real startup is proven.','Source-owned fields are partial backend state, not complete driver/partition allocations.','Instruction identity, complete image linking and hardware remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(count,'KV initialization comparisons passed')
if __name__=='__main__':main()

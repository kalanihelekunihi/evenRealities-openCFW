#!/usr/bin/env python3
"""Compare stock cache admission, ring bytes and transport requests."""
import hashlib,json,struct,subprocess,tempfile,itertools,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 real_copy='--real-copy' in sys.argv
 receipt=BASE/('structured-cache/copy-integration-verification.json' if real_copy else 'structured-cache/verification.json');receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=BASE/'structured-cache/report.json';data=json.loads(report.read_text());obj=BASE/'structured-cache/structured_cache.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 runtime=BASE/'runtime/memory-runtime.o';runtime_report=BASE/'runtime/report.json';assert sha(runtime)==json.loads(runtime_report.read_text())['relocatable_sha256']
 others=[];providers={}
 if real_copy:
  for name,object_name,field in (('structured-cache-copy','structured_cache_copy.o','unit'),('rtos-critical','critical-only.o','selected_object_sha256')):
   path=BASE/(name+'/report.json');r=json.loads(path.read_text());object_path=BASE/(name+'/'+object_name);assert sha(object_path)==(r['units'][0]['object_sha256'] if field=='unit' else r[field]);others.append(object_path);providers[name+'/report.json']=sha(path)
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin'
  ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.log.cache 0x200068f4 (NOLOAD) : { *(.r1.log.cache) } .r1.log.export_buffer 0x20018bc8 (NOLOAD) : { *(.r1.log.export_buffer) } .bss.uxCriticalNesting 0x20007814 (NOLOAD) : { *(.bss.uxCriticalNesting) } /DISCARD/ : { *(.comment) *(.note*) } }')
  names=('r1_structured_log_cache_copy','r1_conn_field6_get','r1_ble_tx_queue_dispatch_type2','r1_event_publish');stock_addresses=(0x41c5c,0x4cb28,0x34070,0x8d8fc)
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=r1_structured_log_cache_append','--defsym=r1_structured_log_mode=0x200068ec',*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(names) if not (real_copy and i==0)],str(obj),str(runtime),*map(str,others),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  assert syms['r1_structured_log_cache']==0x200068f4 and syms['r1_structured_log_export_buffer']==0x20018bc8
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0xe000e000,0x1000)
  candidate.mem_write(0x1000000,binary.read_bytes());seams=dict(zip(stock_addresses,names));seams.update({0x100e000+i*16:n for i,n in enumerate(names)})
  if real_copy:
   del seams[0x41c5c];del seams[0x100e000]
  def hook(uc,address,size,user):
   if address not in seams:return
   name=seams[address];args=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2));value=0
   if name==names[0]:events[id(uc)].append((name,args));uc.mem_write(args[1],bytes([0xab])*args[2])
   elif name==names[1]:events[id(uc)].append((name,));value=0x1234
   elif name==names[2]:events[id(uc)].append((name,args,bytes(uc.mem_read(args[1],args[2]))))
   else:events[id(uc)].append((name,args))
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
  def run(uc,entry,case):
   capacity,read,write,length,mode=case
   uc.mem_write(0x200068ec,bytes([mode]));uc.mem_write(0x200068f4,struct.pack('<4I',0x20010000,capacity,read,write));uc.mem_write(0x20010000,bytes([0x55])*(capacity+32));uc.mem_write(0x20002000,bytes((i*17+3)&255 for i in range(8192)));uc.mem_write(0x20018bc8,bytes(236));events[id(uc)].clear()
   uc.reg_write(UC_ARM_REG_R0,0x20002000);uc.reg_write(UC_ARM_REG_R1,length);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=200000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
   return bytes(uc.mem_read(0x200068f4,16)),bytes(uc.mem_read(0x20010000,capacity+32)),list(events[id(uc)])
  comparisons=0
  for capacity in (0,1,2,8,32,236,256,4096,8192):
   positions=sorted({0,1,capacity//2,max(0,capacity-1),capacity,capacity+1})
   for case in itertools.product((capacity,),positions,positions,(0,1,2,7,8,235,236,4095),range(8)):
    a=run(stock,0x41e80,case);b=run(candidate,syms['r1_structured_log_cache_append'],case);assert a==b,(case,a[0],b[0],a[2],b[2]);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),runtime_report_sha256=sha(runtime_report),provider_reports=providers,actual_cache_copy=real_copy,comparisons=comparisons,scope='Exact ring bytes, write index, strict free-space checks, wrapping, invalid indexes, zero-sized rings and pre-copy transport thresholds with actual source memcpy',limitations=[('Connection getter, BLE transmit and event publish are intercepted; actual cache-copy, critical and memory providers execute.' if real_copy else 'Cache-copy, connection getter, BLE transmit and event publish are intercepted and remain real source dependencies.'),'Ring initialization, concurrency, physical transport and original compiler output remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} structured cache comparisons passed')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Compare erase-on-wrap C writes with locked native code and controlled drivers."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
I=0x20001000;D=0x20001200;OUT=0x20002000
STRINGS={'erase_ring':0x95438,'erase_sdk':0x95464,'reset_ring':0x95488,'reset_sdk':0x954b4,'write_ring':0x954dc,'write_sdk':0x95510}
def main():
 out=BASE/'native-kv-store-put';rp=out/'report.json';obj=out/'native_kv_store_put.o';report=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True)
 assert sha(obj)==report['units'][0]['object_sha256']
 for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 states={};count=0
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin'
  ld.write_text('SECTIONS { '+''.join('.r1.kv.put.log.'+n+' '+hex(a)+' : { *(.r1.kv.put.log.'+n+') } ' for n,a in STRINGS.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  defs={'r1_kv_storage_context':0x2000697c,'r1_kv_storage_driver':0x20006980,'r1_kv_block_cursor':0x20019e49,'r1_kv_block_stride':0x20019e4c,'r1_kv_block_count':0x20019e48,'r1_kv_erase_threshold':0x20019e4a,'r1_structured_log_mode_get':0x100e201,'r1_structured_log_format':0x100e211,'nrf_log_frontend_std_0':0x100e221,'nrf_log_frontend_std_1':0x100e231,'nrf_log_frontend_std_2':0x100e241}
  memory=BASE/'runtime/memory-runtime.o';mr=BASE/'runtime/report.json';assert sha(memory)==json.loads(mr.read_text())['relocatable_sha256']
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_kv_store_put',*['--defsym='+n+'='+hex(a) for n,a in defs.items()],str(obj),str(memory),'-o',str(elf)],check=True,capture_output=True)
  subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for uc in (stock,candidate):
   uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  for n,a in STRINGS.items():
   p=tmp/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.kv.put.log.'+n+'='+str(p),str(elf)],check=True);b=p.read_bytes();assert b==bytes(stock.mem_read(a,len(b)));candidate.mem_write(a,b)
  def ret(uc,v):uc.reg_write(UC_ARM_REG_R0,v&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def hook(uc,address,size,user):
   f=states[id(uc)];args=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if address in (0x100e100,0x100e110,0x100e120,0x100e130):
    erase=address in (0x100e100,0x100e120)
    if erase:
     f['calls'].append(('erase',address,args[0],args[1]));index=f['erase_calls'];f['erase_calls']+=1
    else:f['calls'].append(('write',address,args[0],args[2],bytes(uc.mem_read(args[1],min(args[2],512)))))
    if f['mutation']&1:uc.mem_write(0x2000697c,struct.pack('<I',I+0x100))
    if f['mutation']&2:uc.mem_write(0x20006980,struct.pack('<I',D+0x100))
    if f['mutation']&4:uc.mem_write(0x20019e49,b'\x03');uc.mem_write(0x20019e4c,struct.pack('<I',0xfffffff0))
    if f['mutation']&8:uc.mem_write(0x20019e48,b'\x01')
    ret(uc,(f['erase_result'] if index==f['fail_at'] else 0) if erase else f['write_result'])
   elif address in (0x914ec,0x100e200):
    index=f['mode_calls'];f['mode_calls']+=1;ret(uc,f['modes'][index%len(f['modes'])])
   elif address in (0x91638,0x100e210,0x799c0,0x100e220,0x799c8,0x100e230,0x799d6,0x100e240):
    kind='ring' if address in (0x91638,0x100e210) else 'sdk0' if address in (0x799c0,0x100e220) else 'sdk1' if address in (0x799c8,0x100e230) else 'sdk2'
    if kind=='ring':
     vals=args[:3]
     if args[0]==0x04400000:vals+=args[3:]
     elif args[0]==0x04800000:vals+=args[3:]+list(struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))))
    else:vals=args[:{'sdk0':2,'sdk1':3,'sdk2':4}[kind]]
    f['logs'].append((kind,vals));ret(uc,0)
  for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(uc,ctx=True,driver=True,source=OUT,n=124,cursor=2,threshold=4,blocks=4,stride=4096,base=0x60000,offset=24,erase_result=0,fail_at=0,write_result=0,mutation=0,modes=(0,)):
   for a,v in ((0x2000697c,I if ctx else 0),(0x20006980,D if driver else 0),(0x20019e4c,stride)):uc.mem_write(a,struct.pack('<I',v))
   uc.mem_write(0x20019e48,bytes([blocks,cursor,threshold,0]));uc.mem_write(OUT-4,b'LEFT'+bytes([0xa7])*512+b'RGHT')
   for i in range(2):
    uc.mem_write(I+i*0x100,bytes(52)+struct.pack('<I',(base+i*0x1000)&0xffffffff))
    uc.mem_write(D+i*0x100,bytes(44)+struct.pack('<II',0x100e111+i*32,0x100e101+i*32))
   f=dict(calls=[],logs=[],mode_calls=0,modes=modes,erase_calls=0,erase_result=erase_result,fail_at=fail_at,write_result=write_result,mutation=mutation);states[id(uc)]=f
   uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
   for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(offset,source,n)):uc.reg_write(r,v)
   for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
   uc.emu_start((0x95304 if uc is stock else syms['r1_kv_store_put'])|1,0x20000100,count=100000)
   assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
   assert bytes(uc.mem_read(OUT-4,520))==b'LEFT'+bytes([0xa7])*512+b'RGHT'
   return uc.reg_read(UC_ARM_REG_R0),f['calls'],f['logs'],f['mode_calls'],bytes(uc.mem_read(0x2000697c,8)),bytes(uc.mem_read(0x20019e48,8))
  def compare(**kw):
   nonlocal count
   a=run(stock,**kw);b=run(candidate,**kw);assert a==b,(kw,a,b);count+=1
  for ctx,driver,source,n,cursor in itertools.product((False,True),(False,True),(0,OUT),(0,1,124),(0,4)):compare(ctx=ctx,driver=driver,source=source,n=n,cursor=cursor)
  for cursor in range(256):
   for threshold in (0,1,4,255):
    for blocks in (0,1,4):compare(cursor=cursor,threshold=threshold,blocks=blocks)
  for stride,base,offset,n in itertools.product((0,1,4096,0xffffffff),(0,0x60000,0xfffffff0),(0,24,0xffffffff),(1,24,512,0xffffffff)):compare(stride=stride,base=base,offset=offset,n=n)
  for fail_at,erase_result,write_result,mode in itertools.product(range(5),(0,1,8,0xffffffff),(0,1,8,0xffffffff),range(8)):compare(cursor=4,fail_at=fail_at,erase_result=erase_result,write_result=write_result,modes=(mode,))
  for mutation,fail_at,erase_result,write_result in itertools.product(range(16),(0,2),(0,1),(0,1)):
   for mode in range(8):compare(cursor=4,mutation=mutation,fail_at=fail_at,erase_result=erase_result,write_result=write_result,modes=(mode,))
  for mode in range(256):
   compare(cursor=4,erase_result=1,modes=(mode,));compare(cursor=4,write_result=1,modes=(mode,));compare(cursor=2,write_result=1,modes=(mode,))
  for modes in itertools.product(range(8),repeat=3):
   compare(cursor=4,erase_result=1,modes=modes);compare(cursor=2,write_result=1,modes=modes);compare(cursor=4,modes=modes)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),memory_report_sha256=sha(mr),comparisons=count,scope='Native erase-on-wrap/write policy, error precedence, cursor thresholds, fixed erase spacing versus configured write stride, reloads and callback mutation, mode short circuit, exact descriptors, guards and registers',limitations=['Storage contexts, driver callbacks and mode replies are controlled fixtures; no flash persistence, allocation or live initialization is proven.','Mapped valid context/driver mutation only; controlled erase/write status replies do not prove persistent flash changes.','Instruction identity, whole-image linking and hardware behavior remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(count,'KV put comparisons passed')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Differential chained memory-object lifecycle with actual SDK pool/atomic/critical code."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES=dict(nrf_balloc_init=0x78146,nrf_balloc_alloc=0x780d2,nrf_balloc_free=0x78116,nrf_memobj_pool_init=0x79c98,nrf_memobj_alloc=0x79bfe,nrf_memobj_free=0x79c5e,nrf_memobj_get=0x79c90,nrf_memobj_put=0x79c9c,nrf_memobj_read=0x79cba,nrf_memobj_write=0x79cca)
POOL=0x20002000;CB=POOL+32;STACK=POOL+64;MEM=POOL+128;USER=0x20003000

def main():
 out=BASE/'sdk-memobj';(out/'verification.json').unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'memobj.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 providers={'sdk-critical':('critical-only.o','selected_object_sha256'),'sdk-logger-frontend':('nrf_atomic-selected.o',None),'runtime':('memory-runtime.o','relocatable_sha256')};objects=[obj];reports={}
 for name,(file,key) in providers.items():
  path=BASE/name/'report.json';q=json.loads(path.read_text());o=BASE/name/file;digest=q[key] if key else next(x['object_sha256'] for x in q['units'] if x['source'].endswith('/nrf_atomic.c')) if name=='sdk-logger-frontend' else q.get('selected_object_sha256',q.get('relocatable_sha256'));assert sha(o)==digest,(name,digest);objects.append(o);reports[name+'/report.json']=sha(path)
 comparisons=0;workflows=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .bss.nrf_nvic_state 0x2002c2fc (NOLOAD) : { *(.bss.nrf_nvic_state) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def reset(block,count):
   for u in (stock,candidate):
    u.mem_write(POOL,bytes(2048));u.mem_write(POOL,struct.pack('<5I',CB,STACK,STACK+count,MEM,block));u.mem_write(MEM,bytes([0xa7])*(block*count));u.mem_write(USER,bytes(range(256))*4);u.mem_write(0x2002c2fc,bytes(12));u.mem_write(0xe000e000,bytes(4096))
  def call(name,*args):
   nonlocal comparisons
   results=[]
   for u in (stock,candidate):
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],name
    ret=u.reg_read(UC_ARM_REG_R0) if name in ('nrf_balloc_init','nrf_balloc_alloc','nrf_memobj_pool_init','nrf_memobj_alloc') else None;results.append((ret,bytes(u.mem_read(POOL,2048)),bytes(u.mem_read(USER,1024)),bytes(u.mem_read(0x2002c2fc,12))))
   assert results[0]==results[1],(name,args,results);comparisons+=1;return results[0][0]
  for block,count in itertools.product((12,16,24,32,64),(1,2,4,8)):
   reset(block,count);call('nrf_balloc_init',0);call('nrf_balloc_init',POOL);ptrs=[call('nrf_balloc_alloc',POOL) for i in range(count+1)];assert ptrs[-1]==0
   for ptr in reversed(ptrs[:-1]):call('nrf_balloc_free',POOL,ptr)
   for size in sorted(set((0,1,block-8,block-7,block-4,block-3,(block-4)*count-4,(block-4)*count-3))):
    reset(block,count);call('nrf_memobj_pool_init',POOL);p=call('nrf_memobj_alloc',POOL,size);workflows+=1
    if not p:continue
    cap=((size+4+block-5)//(block-4))*(block-4)-4
    for offset in sorted(set((0,cap//2,cap-1))):
     for length in sorted(set((0,1,cap-offset,cap-offset+1))):
      call('nrf_memobj_write',p,USER,length,offset);call('nrf_memobj_read',p,USER+512,length,offset)
    call('nrf_memobj_get',p);call('nrf_memobj_get',p);call('nrf_memobj_put',p);call('nrf_memobj_put',p)
    p=call('nrf_memobj_alloc',POOL,size)
    if p:call('nrf_memobj_free',p)
 receipt=dict(application_sha256=sha(app),report_sha256=sha(rp),provider_reports=reports,comparisons=comparisons,allocation_workflows=workflows,scope='Actual SDK pool, chained allocation/free, reference atomics, copy and critical code; exhaustion rollback, read/write chunk boundaries and truncation',limitations=['Synthetic valid pool descriptors; native logger pool startup and complete logger backend integration remain gates.','No invalid pointer/double-free/concurrent interleaving proof. Original Arm copy/runtime instruction identity remains unresolved.'],instruction_identity_proven=False);(out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(comparisons,'memory-provider comparisons;',workflows,'allocation workflows')
if __name__=='__main__':main()

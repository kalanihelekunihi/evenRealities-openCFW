#!/usr/bin/env python3
"""Clock IRQ0 vector and pinned dispatch body versus the authenticated native entry."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ,UC_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();STATE=0x20007938;CLOCK=0x40000000;OFFSETS=(0x100,0x104,0x110,0x10c)
def main():
 real_legacy='--real-legacy' in sys.argv;out=BASE/'sdk-nrfx-clock';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'nrfx-clock.o';ep=out/'irq-evidence.json';e=json.loads(ep.read_text());receipt=out/('irq-legacy-integration-verification.json' if real_legacy else 'irq-verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256'] and not r['remaining_symbols']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==e['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';blob=app.read_bytes();assert e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['pseudocode_sha256']==sha(out/e['pseudocode_file'])
 for row in e['rows']:p=out/row['file'];assert sha(p)==row['sha256'];a=int(row['address'],16);assert bytes(json.loads(p.read_text())['data'])==blob[a-0x27000:a-0x27000+row['bytes']]
 lp=BASE/'sdk-clock/report.json';lo=BASE/'sdk-clock/clock.o'
 if real_legacy:
  legacy=json.loads(lp.read_text());assert sha(lo)==legacy['selected_object_sha256']
  for p,d in legacy['inputs'].items():assert sha(ROOT/p)==d,p
 states={};comparisons=0;callbacks=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .bss.r1_sdk_clock_control 0x2002c154 (NOLOAD) : { *(.bss.r1_sdk_clock_control) } .r1.clock.irq0.vector 0x27040 : { *(.r1.clock.irq0.vector) } .bss.r1_sdk_nrfx_clock_control 0x20007938 (NOLOAD) : { *(.bss.r1_sdk_nrfx_clock_control) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=POWER_CLOCK_IRQHandler','--gc-sections','--undefined=r1_power_clock_irq0_vector',*(['--undefined=r1_sdk_clock_irq_handler'] if real_legacy else []),str(obj),*([str(lo)] if real_legacy else []),'-o',str(elf)],check=True,capture_output=True);assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip();subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_power_clock_irq0_vector']==0x27040
  v=t/'vector.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.clock.irq0.vector='+str(v),str(elf)],check=True);assert struct.unpack('<I',v.read_bytes())[0]==syms['POWER_CLOCK_IRQHandler']|1
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(CLOCK,4096)
  stock.mem_write(0x27000,blob);candidate.mem_write(0x1000000,binary.read_bytes());candidate.mem_write(0x27040,v.read_bytes())
  def nrfx_state(u):
   data=bytearray(u.mem_read(STATE,8))
   if real_legacy and struct.unpack_from('<I',data)[0]==(0x584d5 if u is stock else syms['r1_sdk_clock_irq_handler']|1):struct.pack_into('<I',data,0,0xf0f0f0f1)
   return bytes(data)
  def ret(u):u.reg_write(UC_ARM_REG_R0,0xfefefefe);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def hook(u,a,size,user):
   nonlocal callbacks
   if a not in (0x100ed00,0x100ed10):return
   callbacks+=1;f=states[id(u)];ev=u.reg_read(UC_ARM_REG_R0);assert ev in range(4);f['trace'].append(('callback',a,ev,nrfx_state(u),bytes(u.mem_read(0x2002c154,20)) if real_legacy else None,tuple(struct.unpack('<I',bytes(u.mem_read(CLOCK+x,4)))[0] for x in OFFSETS)))
   if f['mutation']==1 and ev==0:u.mem_write(CLOCK+0x104,bytes(4));u.mem_write(CLOCK+0x110,struct.pack('<I',0xffffffff));u.mem_write(STATE,struct.pack('<I',0x100ed11))
   elif f['mutation']==2 and ev==1:u.mem_write(CLOCK+0x100,struct.pack('<I',1));u.mem_write(CLOCK+0x10c,struct.pack('<I',2))
   elif f['mutation']==3 and ev==0:u.mem_write(STATE+5,bytes(1));u.mem_write(CLOCK+0x100,struct.pack('<I',1))
   ret(u)
  def memory(u,access,a,size,value,user):
   if CLOCK<=a<CLOCK+4096:states[id(u)]['trace'].append(('write' if access==UC_MEM_WRITE else 'read',a,size,value if access==UC_MEM_WRITE else bytes(u.mem_read(a,size))))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,memory);u.hook_add(UC_HOOK_MEM_READ,memory)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,events,hf,cal,mask,mutation,repeats):
   states[id(u)]=dict(trace=[],mutation=mutation);u.mem_write(STATE-4,b'\xa7'*4+struct.pack('<I4B',(0x584d5 if u is stock else syms['r1_sdk_clock_irq_handler']|1) if real_legacy else 0x100ed01,1,hf,cal,0xc9)+b'\xb8'*4);u.mem_write(CLOCK,bytes([0x6d])*4096)
   if real_legacy:
    u.mem_write(0x2002c154,struct.pack('<3Bx4I',1,0,0,2,0x20003000,2,0x20003010))
    for i in range(4):u.mem_write(0x20003000+i*8,struct.pack('<2I',0x20003000+(i+1)*8 if i%2==0 else 0,0x100ed01))
   for off,value in zip(OFFSETS,events):u.mem_write(CLOCK+off,struct.pack('<I',value))
   u.mem_write(CLOCK+0x304,struct.pack('<I',mask));results=[]
   for _ in range(repeats):
    u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    vector=struct.unpack('<I',bytes(u.mem_read(0x27040,4)))[0];u.emu_start(vector,0x20000100,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((bytes(u.mem_read(STATE-4,4))+nrfx_state(u)+bytes(u.mem_read(STATE+8,4)),bytes(u.mem_read(CLOCK,4096)),bytes(u.mem_read(0x2002c154,20)) if real_legacy else None,bytes(u.mem_read(0x20003000,32)) if real_legacy else None))
   return results,states[id(u)]['trace']
  for events,hf,cal,mask in itertools.product(itertools.product((0,1,2,0xffffffff),repeat=4),(0,1),(0,1,255),(0,0x1b,0xffffffff)):
   args=(events,hf,cal,mask,0,1);a=run(stock,*args);b=run(candidate,*args);assert a==b,(args,a,b);comparisons+=1
  for bits,hf,mutation,repeats in itertools.product(range(16),(0,1),range(1,4),(1,2,3)):
   args=(tuple((bits>>i)&1 for i in range(4)),hf,1,0,mutation,repeats);a=run(stock,*args);b=run(candidate,*args);assert a==b,(args,a,b);comparisons+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),native_evidence_sha256=sha(ep),selected_object_sha256=sha(obj),comparisons=comparisons,callback_invocations_per_implementation=callbacks//2,vector_bytes_pointer_normalized=4,native_irq_entry='0x30ac8',real_legacy_clock_callback=real_legacy,legacy_report_sha256=sha(lp) if real_legacy else None,handler_pointer_bytes_normalized=4 if real_legacy else 0,scope='Actual pinned IRQ0 dispatcher and HAL helpers entered through source-owned vector word; exact MMIO/callback/state order, duplicate-HF suppression, calibration completion, mutable later events/callback pointer and repeated invocation',limitations=[('Actual legacy clock callback and notification bodies execute; application notification callbacks are fixtures, registers are emulated.' if real_legacy else 'Callback application bodies are fixtures; register values are emulated. No code/SVC/IRQ-body fixture is used.'),'Direct vector calls prove slot binding and callable ABI, not actual Cortex-M exception entry/return, priorities, nesting or physical interrupts.','Remaining vectors, complete startup, calibration analog timing, image linking and byte equality remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'clock IRQ comparisons;',callbacks//2,'callback invocations')
if __name__=='__main__':main()

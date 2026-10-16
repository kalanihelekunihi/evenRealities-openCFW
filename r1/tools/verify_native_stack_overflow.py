#!/usr/bin/env python3
"""Native overflow hook: producer traces, dynamic mode reads and terminal drain."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SECTIONS={'.r1.stack_overflow.ring':0x95c44,'.r1.stack_overflow.nordic':0x95c70};BACKENDS={'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8,'nrf_log_frontend_dequeue':0x796a8}
def main():
 out=BASE/'native-stack-overflow';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'stack-overflow.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;loops=0;busy=0;string_bytes=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in SECTIONS.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');bindings={n:0x100ef01+i*16 for i,n in enumerate(BACKENDS)};subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  for i,(section,a) in enumerate(SECTIONS.items()):
   p=t/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);payload=p.read_bytes();assert payload==bytes(stock.mem_read(a,len(payload)));candidate.mem_write(a,payload);string_bytes+=len(payload)
  kinds={a:n for n,a in BACKENDS.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,user):
   f=states[id(u)]
   if bytes(u.mem_read(a,2))==b'\xfe\xe7':f['terminal']=True;u.emu_stop();return
   if a not in kinds:return
   name=kinds[a];args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
   if name=='r1_structured_log_mode_get':value=f['modes'][f['reads']];f['reads']+=1;trace=('mode',value)
   elif name=='r1_structured_log_format':assert args[0]==0x0c400000 and args[1]==args[2]==0x95c44;trace=('ring',*args)
   elif name=='nrf_log_frontend_std_1':assert args[0]==0x001c0003 and args[1]==0x95c70;trace=('nordic',*args[:3])
   else:
    if f['drain'] is None and f['dequeues']==8:f['busy']=True;u.emu_stop();return
    value=int(f['dequeues']<f['drain']) if f['drain'] is not None else 1;f['dequeues']+=1;trace=('dequeue',value)
   f['trace'].append(trace);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  def case(modes,task,name,drain,basepri=0,primask=0):
   nonlocal comparisons,loops,busy
   results=[]
   for u in (stock,candidate):
    f={'modes':modes,'reads':0,'trace':[],'drain':drain,'dequeues':0,'terminal':False,'busy':False};states[id(u)]=f;u.mem_write(0x20001000,b'task\0'+bytes([0x93])*59);u.mem_write(0x20002000,bytes([0xa5])*112);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,task);u.reg_write(UC_ARM_REG_R1,name);u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_BASEPRI,basepri);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.emu_start((0x95bfc if u is stock else syms['vApplicationStackOverflowHook'])|1,0x20000100,count=100000);assert f['terminal'] or f['busy'];assert u.reg_read(UC_ARM_REG_BASEPRI)==basepri and u.reg_read(UC_ARM_REG_PRIMASK)==primask;results.append((f['trace'],f['terminal'],f['busy'],f['dequeues'],bytes(u.mem_read(0x20001000,64)),bytes(u.mem_read(0x20002000,112)),u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_PRIMASK)))
   assert results[0]==results[1],(modes,task,name,drain,basepri,primask,results);comparisons+=1;loops+=results[0][1];busy+=results[0][2]
  for modes,task,name,drain in itertools.product(itertools.product(range(8),repeat=3),(0,0x20002000,0xffffffff),(0,0x20001000),(0,1,2,4)):case(modes,task,name,drain)
  for modes,drain,basepri,primask in itertools.product(((0,0,0),(1,0,0),(0,4,2),(7,7,7)),(0,4,None),(0,64,224),(0,1)):case(modes,0x20002000,0x20001000,drain,basepri,primask)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,terminal_loop_comparisons=loops,busy_drain_boundaries=busy,string_bytes=string_bytes,scope='Actual native/C hook with all three-read mode sequences, exact producer words/pointers/strings, opaque task/name inputs, finite/busy dequeues and terminal loop; masks preserved',limitations=['Mode, structured/Nordic producers and dequeue are explicit fixtures in this unit. No callee-saved/stack restoration is claimed for a nonreturning hook. A loop entry proves bounded reachability, not physical nontermination or transport delivery.']),indent=2)+'\n');print(comparisons,'overflow comparisons;',loops,'terminal loops;',busy,'busy drain boundaries;',string_bytes,'string bytes')
if __name__=='__main__':main()

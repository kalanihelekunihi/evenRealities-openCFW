#!/usr/bin/env python3
"""Pinned C context port/task selector versus native at SVC/BX-LR boundaries."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
VECTORS={'.r1.application.initial_sp':0x27000,'.r1.application.svc_vector':0x2702c,'.r1.application.pendsv_vector':0x27038}
FIELDS={'pxCurrentTCB':0x2000781c,'pxReadyTasksLists':0x2002ad94,'uxTopReadyPriority':0x2000782c,'xYieldPending':0x20007838}
ENTRIES={'vPortStartFirstTask':0x27238,'SVC_Handler':0x27218,'PendSV_Handler':0x2725c,'vTaskSwitchContext':0x965ac}
def main():
 out=BASE/'rtos-context-port';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'context-port.o';assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;faults=0;overflow=0;switches=0;counts={n:0 for n in ENTRIES}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in VECTORS.items())+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in FIELDS.items()],'--defsym=vApplicationStackOverflowHook=0x100ef01',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  for i,(section,address) in enumerate(VECTORS.items()):
   p=t/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);assert len(p.read_bytes())==4;candidate.mem_write(address,p.read_bytes())
  assert bytes(candidate.mem_read(0x27000,4))==bytes(stock.mem_read(0x27000,4))==struct.pack('<I',0x2003beb8)
  for address,native,name in [(0x2702c,0x27219,'SVC_Handler'),(0x27038,0x2725d,'PendSV_Handler')]:assert struct.unpack('<I',candidate.mem_read(address,4))[0]==syms[name]|1 and struct.unpack('<I',stock.mem_read(address,4))[0]==native
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def word(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def code(u,a,size,user):
   nonlocal switches
   f=states[id(u)];name=f['name'];op=bytes(u.mem_read(a,2))
   if name=='vPortStartFirstTask' and op==b'\x00\xdf':f['boundary']='SVC0';u.emu_stop();return
   if name in ('SVC_Handler','PendSV_Handler') and op==b'\x70\x47':f['boundary']='before exception return';u.emu_stop();return
   if name=='PendSV_Handler' and a==(0x965ac if u is stock else syms['vTaskSwitchContext']&~1):
    switches+=1;f['trace'].append(('select',u.reg_read(UC_ARM_REG_BASEPRI),word(u,0x20001000)));put(u,0x2000781c,f['next_tcb']);u.reg_write(UC_ARM_REG_R0,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a==(0x95bfc if u is stock else 0x100ef00):f['boundary']='overflow hook';f['trace'].append(('overflow',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)));u.emu_stop()
  def invalid(u,access,a,size,value,user):states[id(u)]['fault']=(access,a,value);return False
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
  core=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_LR];fp=[UC_ARM_REG_S0+i for i in range(32)]
  def reset(u,name,primask,basepri,control=0):
   states[id(u)]={'name':name,'trace':[],'boundary':None,'fault':None,'next_tcb':0x20001100};u.mem_write(0x20001000,bytes([0xa5])*0x5000);u.mem_write(0x2000781c,bytes(64));u.mem_write(0x2002ad94,bytes(1120));put(u,0x2000781c,0x20001000);put(u,0x20001000,0x20003000);put(u,0x20001030,0x20004000);u.reg_write(UC_ARM_REG_CONTROL,control);u.reg_write(UC_ARM_REG_IPSR,0 if name in ('vPortStartFirstTask','vTaskSwitchContext') else 11 if name=='SVC_Handler' else 14);u.reg_write(UC_ARM_REG_MSP,0x2003f000);u.reg_write(UC_ARM_REG_PSP,0x20002800);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri);u.reg_write(UC_ARM_REG_FAULTMASK,1)
   for i,reg in enumerate(core):u.reg_write(reg,0x12345600+i)
   for i,reg in enumerate(fp):u.reg_write(reg,0x3f800000+i)
  def execute(name):
   nonlocal comparisons,faults,overflow
   results=[]
   for u in (stock,candidate):
    f=states[id(u)]
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=100000)
    except UcError:assert f['fault'],(name,u is stock,hex(u.reg_read(UC_ARM_REG_PC)))
    assert f['boundary'] or f['fault'] or (name=='vTaskSwitchContext' and u.reg_read(UC_ARM_REG_PC)==0x20000100)
    regs=[u.reg_read(reg) for reg in core]
    # Assembly port has different code addresses but no code-pointer values are outputs.
    if name=='vTaskSwitchContext':
     if not f['boundary'] and not f['fault']:assert u.reg_read(UC_ARM_REG_MSP)==0x2003f000 and [u.reg_read(reg) for reg in core[4:12]]==[0x12345600+i for i in range(4,12)]
     regs=None # void C function permits caller-saved register differences
    results.append((f['boundary'],f['fault'],f['trace'],regs,[u.reg_read(reg) for reg in fp],None if name=='vTaskSwitchContext' and (f['boundary'] or f['fault']) else u.reg_read(UC_ARM_REG_MSP),u.reg_read(UC_ARM_REG_PSP),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_FAULTMASK),u.reg_read(UC_ARM_REG_CONTROL),bytes(u.mem_read(0x20001000,0x5000)),bytes(u.mem_read(0x2000781c,64)),bytes(u.mem_read(0x2002ad94,1120))))
   assert results[0]==results[1],(name,[x[:4] for x in results],[(i,results[0][i],results[1][i]) for i in range(4,11) if results[0][i]!=results[1][i]]);comparisons+=1;faults+=bool(results[0][1]);overflow+=results[0][0]=='overflow hook';counts[name]+=1
  for primask,basepri,control in itertools.product((0,1),(0,64,224),(0,2)):
   for u in (stock,candidate):reset(u,'vPortStartFirstTask',primask,basepri,control)
   execute('vPortStartFirstTask')
   for u in (stock,candidate):assert u.reg_read(UC_ARM_REG_MSP)==0x2003beb8 and u.reg_read(UC_ARM_REG_BASEPRI)==224 and u.reg_read(UC_ARM_REG_R0)==480 and u.reg_read(UC_ARM_REG_PRIMASK)==0 and u.reg_read(UC_ARM_REG_FAULTMASK)==0
  for lr,primask,basepri in itertools.product((0xfffffffd,0xffffffed),(0,1),(0,64,224)):
   for u in (stock,candidate):reset(u,'SVC_Handler',primask,basepri);u.mem_write(0x20003000,struct.pack('<9I',*[0x76543200+i for i in range(8)],lr))
   execute('SVC_Handler')
  for old_fp,new_fp,same,primask,basepri in itertools.product((0,1),(0,1),(0,1),(0,1),(0,64,224)):
   for u in (stock,candidate):
    reset(u,'PendSV_Handler',primask,basepri);u.reg_write(UC_ARM_REG_LR,0xffffffed if old_fp else 0xfffffffd);put(u,0x20001100,0x20003000);u.mem_write(0x20003000,struct.pack('<25I',*[0x87654300+i for i in range(8)],0xffffffed if new_fp else 0xfffffffd,*[0x40000000+i for i in range(16)]));states[id(u)]['next_tcb']=0x20001000 if same else 0x20001100
   execute('PendSV_Handler')
  def init_list(u,a):u.mem_write(a,struct.pack('<5I',0,a+8,0xffffffff,a+8,a+8))
  def append(u,a,item,owner):
   previous=word(u,a+16);u.mem_write(item,struct.pack('<5I',0,a+8,previous,owner,a));put(u,previous+4,item);put(u,a+16,item);put(u,a,word(u,a)+1)
  for occupied,top,repeat,index,suspended,yielding,bad in itertools.product(((),(0,),(0,15),(0,55),(15,55)),(0,15,55),(1,3),(0,1),(0,1,0xffffffff),(0,1,0xffffffff),(-1,0,1,2,3,4)):
   # Top priority must cover all populated lists, as the native API requires.
   if occupied and top<max(occupied):continue
   for u in (stock,candidate):
    reset(u,'vTaskSwitchContext',0,0);u.reg_write(UC_ARM_REG_LR,0x20000101);put(u,0x2000782c,top);put(u,0x20007850,suspended);put(u,0x20007838,yielding)
    for p in range(56):init_list(u,0x2002ad94+p*20)
    for n,p in enumerate(occupied):
     for j in range(repeat):task=0x20001800+n*512+j*128;append(u,0x2002ad94+p*20,task+4,task)
     if index:put(u,0x2002ad94+p*20+4,0x20001804+n*512)
    if bad>=0:put(u,0x20004000+bad*4,0)
   execute('vTaskSwitchContext')
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),driver_sha256=sha(Path(__file__)),comparisons=comparisons,fault_comparisons=faults,overflow_hook_boundaries=overflow,switch_context_fixture_calls_per_implementation=switches//2,comparisons_by_function=counts,source_owned_vector_words=3,full_vector_table_proven=False,scope='Actual pinned C/ARM first-task/SVC/PendSV routines and actual task selector; SVC0/BX-LR boundaries, software FP/core frames, masks, same/other task, ready-list rotation, stack canary selection and assertions',limitations=['PendSV selection is a function fixture in port-isolation cases; kernel selection is tested separately without interception except a bounded overflow hook. Exception-return instructions/SVC0 are not executed here. No physical exception scheduling or complete vector/image identity proof.']),indent=2)+'\n');print(comparisons,'context comparisons;',faults,'faults;',overflow,'overflow boundaries;',counts)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Native ordered selection and lock wrappers; sensor and bus ports are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-motion-selection-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;SEL=0x200076ac;BUS=0x200076b4;D=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'motion-selection-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in (BASE/'native-motion-selection').glob('rea-*.json')}
 for p in (BASE/'native-motion-selection').glob('rea-*.json'):
  n=json.loads(p.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[a-0x27000:a-0x27000+n['returned_bytes']]
 entries={'select':(0x50208,'r1_motion_probe_and_select_provider'),'refresh':(0x5025c,'r1_motion_refresh_selection'),'acquire':(0x5017c,'r1_motion_bus_acquire'),'release':(0x50170,'r1_motion_bus_release'),'lis_probe':(0x6f380,'r1_lis2dw12_probe_wrapper'),'bma_probe':(0x6f1a8,'r1_bma456w_probe_wrapper'),'qma_probe':(0x6f404,'r1_qma6100_probe_wrapper'),'lis_config':(0x6f394,'r1_lis2dw12_configuration_wrapper'),'bma_config':(0x6f1bc,'r1_bma456w_configuration_wrapper'),'qma_config':(0x6f418,'r1_qma6100_configuration_wrapper'),'lis_irq':(0x6f3b2,'r1_lis2dw12_interrupt_noop'),'bma_irq':(0x6f1da,'r1_bma456w_interrupt_noop'),'qma_irq':(0x6f436,'r1_qma6100_interrupt_wrapper'),'initialize':(0x50270,'r1_motion_selected_provider_initialize'),'interrupt':(0x50294,'r1_native_motion_interrupt'),'fifo':(0x502ac,'r1_motion_selected_fifo_read')}
 counts={name:0 for name in entries};observations={name:0 for name in ['acquire','release','lis_probe','bma_probe','qma_probe','lis_config','bma_config','qma_config','qma_irq','lis_fifo','bma_fifo','qma_fifo']};states={};digest=hashlib.sha256()
 with tempfile.TemporaryDirectory(prefix='r1-motion-selection-') as tmp:
  d=Path(tmp);placements=[('lis_table',0x9a730,'.r1.motion.lis.table'),('bma_table',0x9a748,'.r1.motion.bma.table'),('qma_table',0x9a718,'.r1.motion.qma.table')]+[(name,entries[name][0],'.text.'+entries[name][1]) for name in ['lis_probe','bma_probe','qma_probe','lis_config','bma_config','qma_config','lis_irq','bma_irq','qma_irq']]
  ld=d/'layout.ld';ld.write_text('SECTIONS { .selected 0x200076ac : { *(.r1.motion.selected) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } '+''.join('.'+name+' '+hex(a)+' : { *('+section+') } ' for name,a,section in placements)+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  bindings={'r1_lis2dw12_identity_probe':0x754dd,'r1_bma456w_identity_probe':0x53b2d,'r1_qma6100_chip_id':0x86e35,'r1_lis2dw12_configure_boundary':0x75511,'r1_bma456w_configure_boundary':0x53c6d,'r1_qma6100_configure_boundary':0x86e69,'r1_qma6100_irq_boundary':0x86fa9,'r1_lis2dw12_fifo_normalized':0x6f3b5,'r1_bma456w_fifo_normalized':0x6f1dd,'r1_qma6100_fifo_normalized':0x6f449,'r1_lis2dw12_aux16_boundary':0x75291,'r1_lis2dw12_aux20_boundary':0x751b9}
  subprocess.run(['arm-none-eabi-ld','--gc-sections',*[arg for _,name in entries.values() for arg in ['-u',name]],'-T',str(ld),'-e',entries['select'][1],*[f'--defsym={name}={value}' for name,value in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};sections={};table_hashes={}
  for name,a,_ in placements:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);sections[name]=p.read_bytes()
   if name.endswith('table'):assert len(sections[name])==24 and sections[name]==app.read_bytes()[a-0x27000:a-0x27000+24];table_hashes[name]=sha(p)
  ports={0x754dc:'lis_probe',0x53b2c:'bma_probe',0x86e34:'qma_probe',0x75510:'lis_config',0x53c6c:'bma_config',0x86e68:'qma_config',0x86fa8:'qma_irq',0x6f3b4:'lis_fifo',0x6f1dc:'bma_fifo',0x6f448:'qma_fifo',0x1100000:'acquire',0x1100010:'release',0x1100100:'acquire',0x1100110:'release'}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   kind=ports.get(a)
   if not kind:return
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS];result=st['result']
   if kind in ['acquire','release']:st['trace'].append([kind,args[0]]);result=st['result']
   elif kind.endswith('probe'):
    st['trace'].append([kind]);result=st['ids'][['lis_probe','bma_probe','qma_probe'].index(kind)]
    if st['mutation']==1:put(u,BUS,D+32)
   elif kind.endswith('config'):
    st['trace'].append([kind,args[0]]);assert args[0]==25
    if st['mutation']==1:put(u,BUS,D+32)
   elif kind.endswith('fifo'):st['trace'].append([kind,args[:2]]);u.mem_write(args[0],b'\x12\x34\x56\x78')
   else:st['trace'].append([kind])
   if kind=='release' and st['mutation']==2:put(u,SEL,0)
   if not st['side']:observations[kind]+=1
   for reg,value in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook)
   if side:
    for name,a,_ in placements:u.mem_write(a,sections[name])
   machines.append(u)
  defaults=dict(ids=(0x44,0x16,0x90),selected=0,bus=2,result=1,mutation=0,seed=0);cases=[]
  ids=list(itertools.product([0,0x44,0x10044,0xffffffff],[0,0x16,0x10016,0xffffffff],[0,0x90,0x10090,0xfa,0x9f,0xffffffff]))
  for kind,identity,selected,bus,mutation,seed in itertools.product(['select','refresh','initialize'],ids,range(5),range(3),range(3),[0,0xaa]):cases.append(dict(defaults,kind=kind,ids=identity,selected=selected,bus=bus,mutation=mutation,seed=seed))
  for kind,value,bus,mutation,seed in itertools.product(['lis_probe','bma_probe','qma_probe'],[0,1,0x44,0x10044,0xffffffff],range(3),range(3),[0,0xaa]):
   identity=list(defaults['ids']);identity[['lis_probe','bma_probe','qma_probe'].index(kind)]=value;cases.append(dict(defaults,kind=kind,ids=tuple(identity),bus=bus,mutation=mutation,seed=seed))
  for kind,result,bus,mutation,seed in itertools.product(['lis_config','bma_config','qma_config','acquire','release','qma_irq'],[0,1,8,0x80000000,0xffffffff],range(3),range(3),[0,0xaa]):cases.append(dict(defaults,kind=kind,result=result,bus=bus,mutation=mutation,seed=seed))
  for kind,result,seed in itertools.product(['lis_irq','bma_irq'],[0,1,8,0x80000000,0xffffffff],[0,0xaa]):cases.append(dict(defaults,kind=kind,result=result,seed=seed))
  for kind,selected,result,bus,mutation,seed in itertools.product(['interrupt','fifo'],range(5),[0,1,8,0x80000000,0xffffffff],range(3),range(3),[0,0xaa]):cases.append(dict(defaults,kind=kind,selected=selected,result=result,bus=bus,mutation=mutation,seed=seed))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for case in cases:
   kind=case['kind'];results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([case['seed']])*1024);u.mem_write(SP-1024,b'\x96'*2048)
    for i in range(2):u.mem_write(D+i*32,struct.pack('<6I',0,D+128+i*32,0,0,0,0));u.mem_write(D+128+i*32,struct.pack('<4I',0,0,0x1100001+i*256 if case['bus']==2 else 0,0x1100011+i*256 if case['bus']==2 else 0))
    u.mem_write(D+512,bytes(24));put(u,BUS,D if case['bus'] else 0);put(u,SEL,[0,0x9a730,0x9a748,0x9a718,D+512][case['selected']]);states[id(u)]=dict(case,side=side,trace=[])
    args=[D if kind=='fifo' else case['result'],30,0x12345678,0xabcdef01]
    for reg,value in zip(REGS,args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
    results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(SEL,4)).hex(),bytes(u.mem_read(BUS,4)).hex(),bytes(u.mem_read(D,1024)).hex()])
   assert results[0]==results[1],(case,results)
   counts[kind]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,provider_table_sha256=table_hashes,actual_thirteen_bodies_registry_dispatch_and_selected_dispatch=True,only_bus_operations_sensor_leaf_providers_are_fixtures=True,ordered_full_width_ids_fresh_bus_selected_mutations_checked=True,raw_r0_callee_sp_selected_bus_and_ram_checked=True,source_owned_table_bytes=72,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_provider_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()

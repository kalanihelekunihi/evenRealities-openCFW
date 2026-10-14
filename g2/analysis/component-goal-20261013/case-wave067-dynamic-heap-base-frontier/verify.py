from pathlib import Path
import json,struct,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];B=H.parent;F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';E=B/'case-wave065-dma-cancel-call-types/final/case.elf';raw=F.read_bytes()[32:]
with E.open('rb') as f:
 e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
SP=0x20002c88;STOP=0x801ff00;rows=[]
def run(source,size,order):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x8000000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x2000)
 if source:
  for a,d in segs:u.mem_write(a,d)
 else:u.mem_write(0x8000000,raw)
 phase=[''];events=[];low=[SP]
 def code(uc,pc,width,data):
  low[0]=min(low[0],uc.reg_read(UC_ARM_REG_SP))
  if pc==STOP:uc.emu_stop()
 def memory(uc,access,address,width,value,data):
  pc=uc.reg_read(UC_ARM_REG_PC)
  if not source and pc in [0x800afda,0x800afe6]:events.append(dict(phase=phase[0],PC=hex(pc),kind='read' if access==UC_MEM_READ else 'write',address=hex(address),cursor_R1=hex(uc.reg_read(UC_ARM_REG_R1)),argument_R0=hex(uc.reg_read(UC_ARM_REG_R0)),value=value if access==UC_MEM_WRITE else int.from_bytes(uc.mem_read(address,width),'little')))
  if source and width==4 and (address==0x20000198 or 0x20001c88<=address<0x20002888) and phase[0].startswith('free'):events.append(dict(phase=phase[0],PC=hex(pc),kind='read' if access==UC_MEM_READ else 'write',address=hex(address),value=value if access==UC_MEM_WRITE else int.from_bytes(uc.mem_read(address,width),'little')))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory)
 def call(address,args,label):
  phase[0]=label
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args+[0]*4):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,SP);u.mem_write(SP,bytes(4));u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(address|1,0,count=200000);assert u.reg_read(UC_ARM_REG_PC)==STOP
  return u.reg_read(UC_ARM_REG_R0)
 ptrs=[call(syms['case_boot_transport_heap_allocate'] if source else 0x800b3e8,[size],f'allocate{i}') for i in range(3)];assert all(ptrs)
 states=[]
 for index in order:
  call(syms['case_boot_heap_free'] if source else 0x800c030,[ptrs[index]],f'free{index}');states.append(bytes(u.mem_read(0x20000000,0x2888)).hex())
 return dict(pointers=ptrs,states=states,events=events,bounded_stack_bytes=SP-low[0])
for size,order in itertools.product([8,16,32,64],[(0,1,2),(1,0,2),(2,1,0)]):
 a=run(False,size,order);b=run(True,size,order);assert a['pointers']==b['pointers'] and a['states']==b['states']
 for event in a['events']:
  if not event['phase'].startswith('free'):continue
  assert any(x['phase']==event['phase'] and x['kind']==event['kind'] and x['address']==event['address'] and x['value']==event['value'] for x in b['events']),event
 rows.append(dict(request_bytes=size,free_order=list(order),returned_pointers=list(map(hex,a['pointers'])),native_observations=a['events'],source_observations=b['events'],all_free_boundary_RAM_equal=True,native_stack_bytes=a['bounded_stack_bytes'],source_stack_bytes=b['bounded_stack_bytes']))
reads={e['address'] for row in rows for e in row['native_observations'] if e['PC']=='0x800afda' and e['phase'].startswith('free')};writes={e['address'] for row in rows for e in row['native_observations'] if e['PC']=='0x800afe6' and e['phase'].startswith('free')};assert '0x20000198' in reads and len(reads)>1 and writes and '0x20000198' not in writes
r=dict(status='PASS_12_REAL_ALLOCATE_FREE_DYNAMIC_CURSOR_GRAPHS',comparisons=rows,AFDA_actual_read_addresses=sorted(reads),AFE6_actual_write_addresses=sorted(writes),classification='Nonconstant by design: cursor R1 begins at globalhead20000194 and advances throughmutablefree-listnodes; head-onlyliteral198 is not a universal effectiveaddress. AFE6coalescing write uses previousheapnode in validfreefixtures.',missing_inputs_for_particular_runtime_address=['R0 freedblock address and the mutablefree-listchain/head/node-size contents at invocation'],source_ELF_sha256=hashlib.sha256(E.read_bytes()).hexdigest(),limits=['Actualallocator/free/coalescer/scheduler-provider graph, no helperstubs or fabricatedfree-list; RAM startszero in bounded pre-schedulerfixture','AllRAMbelowheapfooter2888 compared at eachfreeboundary; stackexcluded as priorheaptests','Two remaining fixed-base expectations stayuncertain globally; fixture traces areconditionalexamples, notuniversalinvariant/hardwareproof','PhysicalIRQ/reentrancy/asynchronousheapmutation and corrupted/free-invalid-pointer domains notvalidated'])
(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],reads,writes)

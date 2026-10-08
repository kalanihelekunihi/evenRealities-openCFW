"""Locked tickless instruction oracle; timer, scheduler and wake controls explicit."""
from pathlib import Path
import json,struct,hashlib,itertools,argparse
from unicorn import *
from unicorn import arm_const as a
from elftools.elf.elffile import ELFFile
from capstone import *
ROOT=Path(__file__).resolve().parents[7]
p=argparse.ArgumentParser();p.add_argument('--addon',type=Path,required=True);args=p.parse_args()
b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with args.addon.open('rb') as f:
 e=ELFFile(f);ss=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols() if x.name and x['st_shndx']!='SHN_UNDEF'}
assert all(0x50000<=p<=p+len(d)<=0x51000 for p,d in ss)
roles={'confirm':(0x418a00,0x08000100,0),'counter':(0x41f424,0x08000110,0),'compare':(0x41f440,0x08000120,2),'pre':(0x41b5e8,0x08000130,1),'post':(0x41b5f4,0x08000140,1),'enable':(0x41f4b6,0x08000150,1),'clear':(0x41b630,0x08000160,1),'step':(0x418394,0x08000170,1)}
trace={};dis=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
def run(source,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,n in [(0x410000,0x30000),(0x50000,0x1000),(0x08000000,0x2000),(0x20000000,0x40000)]:u.mem_map(p,n)
 if source:
  for p,d in ss:u.mem_write(p,d)
 else:u.mem_write(0x410000,b)
 for p,v in [(0x20027120,f['previous']),(0x20027124,f['period']),(0x20027128,9)]:u.mem_write(p,struct.pack('<I',v))
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_R0,f['expected']);u.reg_write(a.UC_ARM_REG_PRIMASK,f['mask'])
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xa0000000+i)
 calls=[];reads=0;done=[False]
 def hook(cpu,pc,n,_):
  nonlocal reads
  if pc==0x08000000:done[0]=True;cpu.emu_stop();return
  if not source and 0x41b754<=pc<0x41b818:trace[pc]=bytes(cpu.mem_read(pc,n)).hex()
  for name,(orig,stub,argc) in roles.items():
   if pc!=(stub if source else orig):continue
   values=[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(argc)]
   result=f['confirm'] if name=='confirm' else f['pre'] if name=='pre' else f['times'][reads] if name=='counter' else 0
   if name=='counter':reads+=1
   calls.append([name,values,result,cpu.reg_read(a.UC_ARM_REG_PRIMASK)])
   cpu.reg_write(a.UC_ARM_REG_R0,result);cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  ins=next(dis.disasm(bytes(cpu.mem_read(pc,n)),pc,count=1),None)
  if ins and ins.mnemonic=='wfi':calls.append(['synthetic-immediate-wake',[],0,cpu.reg_read(a.UC_ARM_REG_PRIMASK)]);cpu.reg_write(a.UC_ARM_REG_PC,(pc+n)|1)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sy['tickless_sleep'] if source else 0x41b754)|1,0,count=10000);assert done[0]
 return {'calls':calls,'last_counter':bytes(u.mem_read(0x20027120,4)).hex(),'primask':u.reg_read(a.UC_ARM_REG_PRIMASK),'sp':u.reg_read(a.UC_ARM_REG_SP),'callee':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)]}
rows=[]
for period,expected,confirm,pre,wrap,mask in itertools.product([10,1024],[0,1,4,10000],[0,1,2],[0,1],[False,True],[0,1]):
 f={'period':period,'expected':expected,'confirm':confirm,'pre':pre,'previous':0xfffffffc if wrap else 100,'times':[2,24] if wrap else [101,125],'mask':mask};s,c=run(False,f),run(True,f);assert s==c,(f,s,c);rows.append({'fixture':f,'result':s})
used={p+i for p,d in trace.items() for i in range(len(bytes.fromhex(d)))}
Path(__file__).with_name('comparison.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'original_extent':['0x41b754','0x41b818'],'original_body_sha256':hashlib.sha256(b[0x41b754-0x410000:0x41b818-0x410000]).hexdigest(),'addon_sha256':hashlib.sha256(args.addon.read_bytes()).hexdigest(),'visited_body_bytes':len(used),'unvisited':[hex(x) for x in sorted(set(range(0x41b754,0x41b818))-used)],'original_trace':{hex(p):d for p,d in trace.items()},'comparisons':rows,'limits':['Only tickless body is native; sleep-confirm, timer-read/program/enable/clear, pre/post hooks and tick-step are controlled call boundaries with recorded arguments and PRIMASK. WFI is replaced by synthetic immediate wake.','Finite consistent nonzero-period timer fixtures only; no asynchronous timer progression, IRQ wake, architectural WFI waiting, callback side effects, silicon timing or scheduler lifecycle proof.','Counter wrap matches the locked UINT32_MAX-based formula; no correction to modular arithmetic or SDK source-version identity claim.']},indent=2)+'\n');print('PASS tickless',len(rows),'cases',len(used),'of196instruction bytes')

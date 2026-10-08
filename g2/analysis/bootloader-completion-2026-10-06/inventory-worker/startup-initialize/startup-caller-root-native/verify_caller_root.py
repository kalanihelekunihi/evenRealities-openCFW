from pathlib import Path
import json,sys,hashlib
from unicorn import *
from unicorn import arm_const as a
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
N=Path(__file__).resolve().parent;ROOT=next(p for p in N.parents if (p/'AGENTS.md').exists());original=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/pcm2_2-native/verify_root_pcm22_state.py'
code=original.read_text();prefix=code.split('fixtures=[]',1)[0].replace(';u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)','');env={'__file__':str(original),'__name__':'root_fixture'};exec(prefix,env);u_run=env['run'];sy=env['symbols'];segments=env['segments'];blob=env['blob'];env['entries']['init']=('opencfw_provider_41fa50',0x41fa50,0x41fa98)
# Recover the actual callsite/LR from linked caller instructions rather than guessing.
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);start=sy['opencfw_provider_41fa50']&~1;data=next(s['data'][start-s['address']:] for s in segments if s['address']<=start<s['address']+len(s['data']));call=next(i for i in md.disasm(data,start) if i.mnemonic=='bl' and int(i.op_str[1:],0)==(sy['opencfw_boot_startup_initialize_abi']&~1));resume_source=call.address+call.size
original_uc=env['Uc'];current_source=False;extra_events=[];caller_state={};visited_stock=set()
post={'power-config':('opencfw_boot_startup_power_configure',0x41c86c),'temperature':('opencfw_boot_startup_temperature',0x41ca2c),'descriptor':('opencfw_boot_startup_clock_descriptor',0x422416),'clock-select':('opencfw_boot_startup_clock_select',0x4222a0)}
def machine(*args,**kwargs):
 u=original_uc(*args,**kwargs);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);enabled=[False]
 def watch(cpu,pc,size,_):
  if not enabled[0]:cpu.reg_write(a.UC_ARM_REG_C1_C0_2,0xf00000);enabled[0]=True
  if not current_source:visited_stock.update(range(pc,pc+size))
  if pc==(sy['opencfw_boot_startup_initialize_abi']&~1 if current_source else 0x41c4b4):caller_state['at_root']=[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in [5,7]];caller_state['root_sp']=cpu.reg_read(a.UC_ARM_REG_SP)
  if pc==(resume_source if current_source else 0x41fa5c):caller_state['complete']=True
  if not caller_state.get('complete'):return
  if not current_source and pc==0x4156ac:
   dest=cpu.reg_read(a.UC_ARM_REG_R0);src=cpu.reg_read(a.UC_ARM_REG_R1);count=cpu.reg_read(a.UC_ARM_REG_R2);assert count==20;cpu.mem_write(dest,bytes(cpu.mem_read(src,count)));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  for kind,(name,stock) in post.items():
   if pc!=(sy[name]&~1 if current_source else stock):continue
   regs=[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(3)]
   if kind=='temperature':extra_events.append([kind,cpu.reg_read(a.UC_ARM_REG_S0)]);cpu.mem_write(regs[0],bytes(8))
   elif kind=='descriptor':extra_events.append([kind,bytes(cpu.mem_read(regs[0],20)).hex()])
   else:extra_events.append([kind,*regs[:2 if kind=='power-config' else 3]])
   cpu.reg_write(a.UC_ARM_REG_R0,0);cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
 u.hook_add(UC_HOOK_CODE,watch);return u
env['Uc']=machine
fixtures=[]
for rev in [32,34,36]:
 for variant in [0,1,2,3,4]:
  for flags in [0,0x7f]:
   for saved in [0,1]:fixtures.append(dict(revision=rev,variant=variant,gate=3,seed=0xffffffff,saved=saved,present=True,irq=0,clock_flags=flags,ambient_r5=0xa5b6c7d8,ambient_r7=0x11223344,clock_guard=0))
for selector in [0x210,0x245]:
 for failure in [0,7]:fixtures.append(dict(revision=34,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=0,clock_flags=0x7f,ambient_r5=0xa5b6c7d8,ambient_r7=0x11223344,clock_guard=0,cached=False,fail_selector=selector,failure=failure,gate29=8,active=1))
rows=[]
for f in fixtures:
 results=[]
 for source in [False,True]:
  current_source=source;extra_events=[];caller_state={};x=u_run(source,'init',f);x['post_events']=extra_events;x['ambient_at_root']=caller_state.get('at_root');assert caller_state.get('complete')
  # Outer function is void; volatileR0–R3 are not a caller-visible contract.
  x.pop('registers');x.pop('ret');results.append(x)
 if results[0]!=results[1]:(N/'caller-root-failure.json').write_text(json.dumps({'fixture':f,'stock':results[0],'source':results[1]},indent=2));raise AssertionError((f,results))
 rows.append({'fixture':f,'result':results[0]})
r={'status':'PASS_CALLER_NATIVE_ROOT_COUPLED','cases':len(rows),'candidate_sha256':hashlib.sha256(env['args'].elf.read_bytes()).hexdigest(),'original_sha256':hashlib.sha256(blob).hexdigest(),'stock_caller_visited_bytes':len(visited_stock&set(range(0x41fa50,0x41fa98))),'root_visited_bytes':len(visited_stock&set(range(0x41c4b4,0x41c7de))),'comparisons':rows,'limits':['Caller41fa50 and root41c4b4 execute actual original/native bodies. Root descendants retain existing native/stock models with synthetic MMIO acknowledgement and absent ROM40/48 contracts.','Four post-root child families are deliberately controlled; root interior is not cut. Original4156ac20-byte descriptor copy modeled due existing Unicorn fixture limitation; native inline copy executes.','Void callerR0–R3/return omitted; callee-savedR4–R11,SP,PRIMASK,memory/effects, post-childargs and incomingR5/R7 at root compare. No hardware, scheduler, all-input or byte-identity claim.']};env['args'].output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['root_visited_bytes'])

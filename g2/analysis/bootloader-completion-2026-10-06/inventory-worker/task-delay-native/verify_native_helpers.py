from pathlib import Path
import importlib.util,json,itertools,hashlib,argparse
from elftools.elf.elffile import ELFFile
from unicorn import UC_HOOK_MEM_WRITE
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());B=R/'g2/build/bootloader-completion/iar-format-native-integrated/dbbd73cfd6b5f15fb1ec4dce44ee4c67d56d1ad4d1c7fef4915f112f550da258/candidate.elf'
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=B);ap.add_argument('--output',type=Path,default=N/'native-helpers-comparison.json');args=ap.parse_args();B=args.elf
spec=importlib.util.spec_from_file_location('timer',R/'g2/components/bootloader/thread_creation/verify_timer_wait.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);v=t.v;v.ENTRIES['cmsis_delay']=0x416378;_,segs,sy=v.elf.elf_info(B)
extra=[]
if 'opencfw_cmsis_delay' not in sy:
 with Path('/tmp/opencfw-task-delay-native-helpers.elf').open('rb') as f:
  e=ELFFile(f);extra=[dict(address=s['p_vaddr'],memory_size=s['p_memsz'],data=s.data(),flags=s['p_flags']) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];ss={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};sy.update(ss)
sy['opencfw_boot_cmsis_delay']=sy['opencfw_cmsis_delay']
class Machine(t.Machine):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.yields=[];self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def write(self,cpu,access,p,size,value,_):
  if p==0xe000ed04:self.yields.append([size,value])
rows=[];trace={}
for now,ticks,cursor,running,mask,basepri,ipsr,pending in itertools.product([0,17,0xfffffff0],[0,1,32,0xffffffff],[False,True],[0,1],[0,1],[0,48],[0,16],[0,1]):
 pair=[Machine(),Machine(True,segs+extra,sy)];results=[]
 for m in pair:
  t.init(m,now,cursor);m.w(0x20027150,running);m.w(0x20027158,pending);m.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK,mask);m.cpu.reg_write(v.a.UC_ARM_REG_BASEPRI,basepri);m.cpu.reg_write(v.a.UC_ARM_REG_IPSR,ipsr);r=m.run('cmsis_delay',[ticks]);x=t.state(m);x['return']=r['return'];x['yields']=m.yields;x['mask']=m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK);results.append(x)
 if results[0]!=results[1]:(N/'native-helpers-failure.json').write_text(json.dumps({'fixture':[now,ticks,cursor,running,mask,basepri,ipsr,pending],'stock':results[0],'source':results[1]},indent=2));raise AssertionError((now,ticks,cursor,running,mask,basepri,ipsr,pending))
 trace.update(pair[0].trace);rows.append({'fixture':[now,ticks,cursor,running,mask,basepri,ipsr,pending],'result':results[0]})
r={'status':'PASS_DELAY_WITH_NATIVE_GUARD_SCHEDULER_LISTS','cases':len(rows),'base_candidate_sha256':v.sha(B),'delay_module_sha256':v.sha('/tmp/opencfw-task-delay-native-helpers.elf'),'source_sha256':v.sha(N/'task_delay.c'),'comparisons':rows,'original_trace':trace,'limits':['Actual guard, suspend, task-list removal/insertion, resume, critical/masking and PendSV-request stores execute original/native bodies. Source side loads compiled candidate/modules only.','Coherent syntheticTCB/lists,ticks, pending-yield flag, IPSR/masks and running state; no automatic exception delivery, real task switch, tick units in time or hardware lifecycle proof.','Finite and wrapped deadlines, UINT_MAX nonindefinite behavior, rejection and zero-delay behavior compared; fatal scheduler-suspended branch covered separately with explicit child contracts.']};args.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])

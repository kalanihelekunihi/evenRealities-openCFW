from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'should_enter':(0x44b15c,0x44b180),'has_requests':(0x44b188,0x44b1c8),'reinitialize_retained':(0x44b4dc,0x44b4ee),'gated_path':(0x44b158,0x2007f000)}
def run(native,kind,state,reset):
 u=machine();w(u,0x40008858,state);w(u,0x4000885c,reset);writes=[];calls=[]
 def code(u,a,n,d):
  if not native and a==entries[kind][1]:u.emu_stop()
  if a==0x44b1d0:calls.append('active_recovery')
 def write(u,ac,a,n,v,d):writes.append([a,n,v])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x40021fff)
 u.emu_start((sym['clock_reset_'+kind] if native else entries[kind][0])|1,0x2007f000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==(0x2007f000 if native else entries[kind][1])
 return dict(value=None if kind in ['reinitialize_retained','gated_path'] else u.reg_read(UC_ARM_REG_R0),retained=word(u,0x40008858),writes=writes,calls=calls)
rows=[]
for state,reset in itertools.product([0,0xffffffff,0x5af00000,0x5af0003f,0x5af0ffff,0x5af10000,0x00005af0],[0,1,2,3,0xffffffff]):
 for kind in ['should_enter','has_requests','reinitialize_retained']:
  o=run(False,kind,state,reset);n=run(True,kind,state,reset);assert o==n,(kind,state,reset,o,n);rows.append(dict(kind=kind,state=state,reset=reset,output=o))
for low,upper in itertools.product(range(64),[0,0x5af00000,0xffff0000,0x0000ffc0]):
 o=run(False,'has_requests',upper|low,0);n=run(True,'has_requests',upper|low,0);assert o==n;rows.append(dict(kind='has_requests',state=upper|low,reset=0,output=o))
for state,reset in itertools.product([0,0xffffffff,0x5af00000,0x5af0003f,0x5af0ffff,0x5af10000,0x00005af0],[0,1,2,3,0xffffffff]):
 if not(reset&2) and state>>16==0x5af0 and state&63:continue
 o=run(False,'gated_path',state,reset);n=run(True,'gated_path',state,reset);assert o==n,(state,reset,o,n);rows.append(dict(kind='gated_path',state=state,reset=reset,output=o))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Direct bounded instruction-block comparisons at real continuation addresses, not complete recovery-function implementation.','Includes actual retained-register write order; no active clock recovery or physical readiness validation.']),separators=(',',':'))+'\n');print('PASS',len(rows),'clock gate/block comparisons')

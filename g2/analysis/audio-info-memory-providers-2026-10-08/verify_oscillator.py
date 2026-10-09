from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
def run(native,action,value=None,pattern=0,cap1=0,cap2=0,mask=0,skip_request=False):
 u=machine();u.reg_write(UC_ARM_REG_R0,action);u.reg_write(UC_ARM_REG_R1,0 if value is None else 0x20006000);u.reg_write(UC_ARM_REG_PRIMASK,mask);w(u,0x20006000,0 if value is None else value);u.mem_write(0x200001e0,bytes([cap1]));w(u,0x200001e4,cap2)
 for a in [0x40020120,0x40020128,0x4002012c]:w(u,a,pattern)
 calls=[];writes=[];pending=[]
 def code(u,a,n,d):
  if pending and a==pending[-1][0]:_,i=pending.pop();calls[i]['return']=u.reg_read(UC_ARM_REG_R0)
  if a in [0x4807a0,0x4c44bc,0x4c4530]:
   calls.append(dict(name={0x4807a0:'delay',0x4c44bc:'request',0x4c4530:'release'}[a],args=[u.reg_read(UC_ARM_REG_R0)] if a==0x4807a0 else [u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]));pending.append((u.reg_read(UC_ARM_REG_LR)&~1,len(calls)-1))
 def write(u,ac,a,n,v,d):writes.append([a,n,v&((1<<(8*n))-1)])
 def invalid(u,ac,a,n,v,d):raise AssertionError(('unmapped',native,action,hex(u.reg_read(UC_ARM_REG_PC)),hex(a)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x4021ffff);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 u.emu_start((sym['audio_oscillator_control'] if native else 0x4809c4)|1,0x2007f000,count=3000000)
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,('limit',native,action,hex(u.reg_read(UC_ARM_REG_PC)))
 for c in calls:
  if c['name']=='delay':c.pop('return',None)
 return dict(status=u.reg_read(UC_ARM_REG_R0),calls=calls,writes=writes,primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for action,value,pattern,(cap1,cap2),mask in itertools.product(range(5),[None,0,1,2,255],[0,0xffffffff,0x12345678],[(0,0),(255,0xffffffff)],[0,1]):
 case=dict(action=action,value=value,pattern=pattern,cap1=cap1,cap2=cap2,mask=mask);o=run(False,**case);n=run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
for action,value,pattern in itertools.product([5,6,7,255,256,257],[None,0,1,2,3,7,8],[0,0xffffffff]):
 case=dict(action=action,value=value,pattern=pattern);o=run(False,**case);n=run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
(D/'oscillator-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Actual delay/clock-manager providers execute; clock-manager status propagation is not stubbed.','Synthetic capacitance/control words, not measured crystal frequency/startup or pad drive.','Only stored write effects and meaningful status/calls compared; scratch registers/stack probes outside scope.']),separators=(',',':'))+'\n');print('PASS',len(rows),'oscillator comparisons')

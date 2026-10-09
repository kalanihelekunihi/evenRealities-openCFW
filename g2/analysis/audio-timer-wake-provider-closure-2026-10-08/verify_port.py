from pathlib import Path
import json,itertools,hashlib
D=Path(__file__).resolve().parent
# Reuse only machine/fixture definitions, not another test suite's execution.
exec((D/'verify.py').read_text().split('for priority,suspended,kind,event_index,ready_existing,pending_existing in itertools.product')[0])
rows=[]
targets={'mask_set':(0x5fa0a4,'audio_port_mask_set'),'mask_restore':(0x5fa0ba,'audio_port_mask_restore'),'enter':(0x4420d0,'stock_enter_critical'),'exit':(0x4420e8,'stock_exit_critical'),'missed_yield':(0x4555e6,'stock_missed_yield')}
def run(native,kind,mask,nesting=0,argument=0,pending=0):
 u,w,word,append=fixture(54,1,'delayed');w(0x2000309c,nesting);w(0x20074a44,pending);u.reg_write(UC_ARM_REG_BASEPRI,mask);u.reg_write(UC_ARM_REG_R0,argument);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);boundary=[]
 def hook(u,a,n,d):
  if a==0x4420f6:boundary.append('before_fatal_store');u.emu_stop();return
  assert a not in [0x4420bc,0x45537e],'unexpected yield/wake assertion'
 u.hook_add(UC_HOOK_CODE,hook);a=targets[kind][0] if not native else sym[targets[kind][1]];u.emu_start(a|1,0x2007f000,count=10000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
 return dict(boundary=boundary,nesting=word(0x2000309c),basepri=u.reg_read(UC_ARM_REG_BASEPRI),pending=word(0x20074a44),return_value=u.reg_read(UC_ARM_REG_R0) if kind=='mask_set' else None,sp_restored=u.reg_read(UC_ARM_REG_SP)==0x2007e000 if not boundary else None)
cases=[]
for kind,mask,nesting in itertools.product(['enter','exit'],[0,16,32,48,64,128,240],[0,1,2,0xffffffff]):cases.append(dict(kind=kind,mask=mask,nesting=nesting))
for mask in [0,16,32,48,64,128,240]:cases.append(dict(kind='mask_set',mask=mask))
for arg in [0,16,32,48,64,128,0xffffffff]:cases.append(dict(kind='mask_restore',mask=48,argument=arg))
for pending in [0,1,2,0xffffffff]:cases.append(dict(kind='missed_yield',mask=48,pending=pending))
for c in cases:
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
(D/'port-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Named MRS/MSR/DSB/ISB reconstructed source, no retained executable array.','Zero nesting exit stops before actual fault-store instruction; fault not executed or turned into success.','No IRQ delivery,PendSV,task switch or elapsed-time model.']},indent=2)+'\n');print('PASS',len(rows),'port-helper comparisons')

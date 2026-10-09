from pathlib import Path
import itertools,json
D=Path(__file__).resolve().parent
exec(compile((D/'verify.py').read_text().split('rows=[]')[0],str(D/'verify.py'),'exec'))
def capture(u):return dict(status=u.reg_read(UC_ARM_REG_R0),table=bytes(u.mem_read(0x20073324,56)).hex(),pad15=word(u,0x4001003c),pll=word(u,0x400204d8),hfrc_force=word(u,0x40004044),primask=u.reg_read(UC_ARM_REG_PRIMASK))
def sequence(native,op,case):
 u=run(native,op=op,**case,expose=True);states=[capture(u)];waits=[]
 def code(u,a,n,d):
  if a==0x480826:waits.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]])
 u.hook_add(UC_HOOK_CODE,code)
 next_ops=[('hfrc2_force',1),('hfrc2_force',0)] if op=='hfrc2_force' else [('ext_request',52),('ext_release',52)] if op=='ext_request' else [('pll_power_enable',0),('pll_power_disable',0)]
 for name,arg in next_ops:
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.reg_write(UC_ARM_REG_R0,arg);u.emu_start((sym['audio_'+name] if native else entries[name])|1,0x2007f000,count=3000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;states.append(capture(u))
 return dict(states=states,subsequent_waits=waits)
rows=[]
for ready,mask in itertools.product([0,1],[0,1]):
 case=dict(ready=ready,mask=mask,pattern=0,value=1);o=sequence(False,'hfrc2_force',case);n=sequence(True,'hfrc2_force',case);assert o==n;assert [x['status'] for x in o['states']]==[0 if ready else 4,0,0];assert not o['subsequent_waits'];rows.append(dict(op='hfrc2_force',inputs=case,**o))
for other,mask in itertools.product([0,1],[0,1]):
 case=dict(other=other,mask=mask,pattern=0xdeadbeef);o=sequence(False,'ext_request',case);n=sequence(True,'ext_request',case);assert o==n;assert [x['pad15'] for x in o['states']]==[10,10,10 if other else 3];rows.append(dict(op='ext_request',inputs=case,**o))
for major,mask in itertools.product([0x21,0x22],[0,1]):
 case=dict(major=major,mask=mask,pattern=0xffffffff);o=sequence(False,'pll_power_enable',case);n=sequence(True,'pll_power_enable',case);assert o==n;assert o['states'][2]['pll']&0xc0000000==0xc0000000;rows.append(dict(op='pll_power_enable',inputs=case,**o))
(D/'sequence-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Timeout inputs are synthetic,actual delay/wait bodies execute.','Repeat force-on returns0 based on the command bit,not observed ready state.','GPIO last-user cleanup programs disabled configuration3,not saved-pad restoration.']),indent=2)+'\n');print('PASS',len(rows),'leaf request/release sequences')

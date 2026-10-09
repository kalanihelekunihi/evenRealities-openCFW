from pathlib import Path
import itertools,json
D=Path(__file__).resolve().parent
exec(compile((D/'verify_config.py').read_text().split('rows=[]')[0],str(D/'verify_config.py'),'exec'))
ops={'hfrc2_request':0x4c4086,'hfrc2_release':0x4c420c,'syspll_request':0x4c427e,'syspll_release':0x4c43ec}
def snapshot(u,family):
 return dict(status=u.reg_read(UC_ARM_REG_R0),valid=bytes(u.mem_read(0x20004537 if family=='hfrc2' else 0x20074f55,1)).hex(),config=bytes(u.mem_read(0x20073f3c if family=='hfrc2' else 0x20073f48,12)).hex(),selected_hz=word(u,0x20074254 if family=='hfrc2' else 0x20074258),table=bytes(u.mem_read(0x20073324,56)).hex(),flags=bytes(u.mem_read(0x20074f55,7)).hex(),handle=word(u,0x2007425c),driver=bytes(u.mem_read(0x200740f4,8)).hex(),pll=word(u,0x400204d8),hf2_force=word(u,0x40004044),primask=u.reg_read(UC_ARM_REG_PRIMASK))
def sequence(native,case,ready,lock):
 family=case['family'];u=run(native,**case,expose=True);states=[snapshot(u,family)];waits=[];pending=[]
 def code(u,a,n,d):
  if pending and a==pending[-1][0]:_,i=pending.pop();waits[i]['status']=u.reg_read(UC_ARM_REG_R0)
  if a==0x480826:waits.append(dict(args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]));pending.append((u.reg_read(UC_ARM_REG_LR)&~1,len(waits)-1))
 u.hook_add(UC_HOOK_CODE,code);w(u,0x40004030,(1<<24) if ready else 0);w(u,0x40020060,0xf0000 if ready else 0);w(u,0x400204e4,lock)
 if states[0]['status']==0:
  for name in [family+'_request',family+'_request',family+'_release']:
   u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.reg_write(UC_ARM_REG_R0,52);u.emu_start((sym['audio_'+name] if native else ops[name])|1,0x2007f000,count=12000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;states.append(snapshot(u,family))
 return dict(states=states,waits=waits)
scenarios=[dict(family='hfrc2',hz=0),dict(family='hfrc2',hz=196608000),dict(family='hfrc2',hz=250000000),dict(family='hfrc2',hz=196608000,explicit=1,ref=0),dict(family='syspll',hz=48000000),dict(family='syspll',hz=96000000),dict(family='syspll',hz=48000000,explicit=1,ref=1),dict(family='syspll',hz=48000000,explicit=1,ref=1,bad=1),dict(family='syspll',hz=48000000,explicit=1,ref=0)]
rows=[]
for case,ready,lock in itertools.product(scenarios,[0,1],[0,1]):
 o=sequence(False,case,ready,lock);n=sequence(True,case,ready,lock);assert o==n,(case,ready,lock,o,n)
 states=o['states']
 if case.get('ref')==0 and case.get('explicit'):assert len(states)==1 and states[0]['status']==7 and states[0]['valid']=='00'
 if case.get('bad') and ready:assert [s['status'] for s in states]==[0,6,6,0] and states[1]['handle']==0
 if case['family']=='syspll' and case.get('ref',1)==1 and not case.get('bad') and ready and not lock:assert [s['status'] for s in states]==[0,4,0,0] and states[1]['handle'] and not states[-1]['handle']
 rows.append(dict(config=case,stock_board=dict(hs_hz=0,ls_hz=32768,external_hz=12000000),synthetic_power_ready=ready,synthetic_lock=lock,**o))
(D/'reachability-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Control flow through actual successful stock configuration is proved offline; physical power/lock faults and timing are synthetic, not observed hardware incidents.','Automatic clock generation executes original instructions in the stock guest and reconstructed native generators in the source guest; original math-library dependencies remain.','No BLE/app dispatch path to these internal HAL calls or async IRQ reachability is claimed.']),indent=2)+'\n');print('PASS',len(rows),'stock-configuration-to-request comparisons')

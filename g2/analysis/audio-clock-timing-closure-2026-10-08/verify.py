from pathlib import Path
import json,itertools,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'save_irq':0x473940,'delay_cycles':0x40,'delay_us':0x4807a0,'wait4':0x4807fc,'wait5':0x480826}
def run(native,c):
 u=machine();
 if native:require_source_code(u)
 op=c['op'];u.reg_write(UC_ARM_REG_PRIMASK,c.get('mask',0));u.reg_write(UC_ARM_REG_FPSCR,c.get('fpscr',0));w(u,0x40021000,c.get('performance',0)<<3);w(u,0x400204e4,c.get('initial',0));reads=[];delays=[];cycles=[];cut=[];active_spin=[]
 def code(u,a,n,d):
  if active_spin and a==active_spin[0]:active_spin.clear()
  if a in [0x4807a0,sym['audio_delay_us']&~1]:delays.append(u.reg_read(UC_ARM_REG_R0))
  if a in [0x40,sym['audio_delay_cycles']&~1]:
   # Original loop branches back to its entry each iteration; count only call
   # entry using its actual LR, not every loop iteration. Native entry may do so too.
   lr=u.reg_read(UC_ARM_REG_LR)
   if not active_spin:
    active_spin.append(lr&~1)
    cycles.append(dict(count=u.reg_read(UC_ARM_REG_R0),entry=(a,lr)))
    if c.get('cut_spin'):cut.append('before_spin');u.emu_stop()
 def rd(u,ac,a,n,v,d):
  if c.get('change_at')==len(reads)+1:w(u,a,c.get('changed',1))
  reads.append(word(u,a))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,rd,begin=0x400204e4,end=0x400204e7)
 if op in ['delay_us','delay_cycles']:args=[c['count']]
 elif op.startswith('wait'):args=[c['budget'],0x400204e4,c.get('bits',1),c.get('expected',1),c.get('equal',1)]
 else:args=[]
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 if len(args)==5:w(u,0x2007e000,args[-1])
 u.emu_start((sym['audio_'+op] if native else entries[op])|1,0x2007f000,count=1000000);assert cut or u.reg_read(UC_ARM_REG_PC)==0x2007f000,c
 return dict(status=u.reg_read(UC_ARM_REG_R0) if op in ['save_irq','wait4','wait5'] else None,primask=u.reg_read(UC_ARM_REG_PRIMASK),fpscr=u.reg_read(UC_ARM_REG_FPSCR),reads=reads,delays=delays,cycles=[v['count'] for v in cycles],cut=cut,sp=None if cut else u.reg_read(UC_ARM_REG_SP),final_word=word(u,0x400204e4))
rows=[]
def compare(c):
 o=run(False,c);n=run(True,c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for mask,fpscr in itertools.product([0,1],[0,0xa000009f]):compare(dict(op='save_irq',mask=mask,fpscr=fpscr))
for count,mask in itertools.product([1,2,3,32,100],[0,1]):compare(dict(op='delay_cycles',count=count,mask=mask))
for count,performance,fpscr in itertools.product([0,1,2,5,10,96,1000],[0,1,2,3],[0,1<<22,1<<24,0xa000009f]):compare(dict(op='delay_us',count=count,performance=performance,fpscr=fpscr))
# Huge counts stop at the actual spin entry, never synthesize its return.
for count,performance,fpscr in itertools.product([0x01000001,0x07ffffff,0x08000000,0xffffffff],[0,2],[0,1<<22,3<<22,0xa000009f]):compare(dict(op='delay_us',count=count,performance=performance,fpscr=fpscr,cut_spin=True))
for op,budget,initial,expected,equal,change,mask in itertools.product(['wait4','wait5'],[0,1,3],[0,1],[0,1,2],[0,1,2,255,256],[0,1,2,4],[0,1]):compare(dict(op=op,budget=budget,initial=initial,expected=expected,equal=equal,change_at=change,changed=1-initial,mask=mask))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Native IRQ,delay,ITCM spin and status waits execute reconstructed source; original guest uses authenticated ITCM/init records.','Huge delay inputs stop before spin entry and compare actual count/FPSCR only; no fabricated spin completion.','MMIO status transitions at selected reads are synthetic, not asynchronous hardware/IRQ evidence.','Zero standalone spin count is excluded: original underflows and requires2^32 iterations; caller delay establishes positive-count precondition.','Source names microsecond units; physical cycle/elapsed-time accuracy and complete M55 timing unverified.']),separators=(',',':'))+'\n');print('PASS',len(rows),'timing/poll comparisons')

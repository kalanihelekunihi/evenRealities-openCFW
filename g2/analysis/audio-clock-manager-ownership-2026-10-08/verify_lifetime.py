from pathlib import Path
import itertools,json
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
def invoke(u,a,args):
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(a|1,0x2007f000,count=3000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;return u.reg_read(UC_ARM_REG_R0)
def state(u):return dict(users_low=word(u,0x20073334),users_high=word(u,0x20073338),control=word(u,0x4002012c),stabilizing=bytes(u.mem_read(0x20074f56,1)).hex(),counter=word(u,0x20074260),retained=word(u,0x40008858),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for drive,other,mask in itertools.product([1,2,8,0,3,7],[0,1],[0,1]):
 u=machine();u.mem_write(0x20073324,b'\0'*56);w(u,0x20073334,other);u.mem_write(0x200001cc,b'\0');w(u,0x200001d0,24000000);u.mem_write(0x20074f56,b'\0');w(u,0x20074260,0);w(u,0x4002012c,0);w(u,0x40008858,0x5af00000);w(u,0x20006000,drive);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 trace=[]
 def code(u,a,n,d):
  if a in [0x4c44bc,0x4c3d9e,0x4c37fe,0x4c4530,0x4c3e9a,0x4809c4]:trace.append(dict(address=hex(a),args=[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)]))
 u.hook_add(UC_HOOK_CODE,code)
 before=state(u);s1=invoke(u,0x4809c4,[5,0x20006000]);after=state(u);assert s1==(6 if drive in [1,2,8] else 0);assert after['users_high']&(1<<20);assert after['users_low']==other
 s2=invoke(u,0x4809c4,[5,0x20006000]);repeat=state(u);assert s2==s1 and repeat['users_high']==after['users_high'];assert repeat['stabilizing']=='00' and repeat['counter']!=0
 sr=invoke(u,0x4809c4,[6,0]);released=state(u);assert sr==0 and released['users_high']==0 and released['users_low']==other;assert released['primask']==mask
 if not other:assert released['control']&1==0 and released['counter']==0
 rows.append(dict(drive=drive,other_user=other,initial_primask=mask,statuses=[s1,s2,sr],before=before,after=after,repeat=repeat,released=released,trace=trace))
(D/'lifetime-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),validation='original-instruction sequence assertions, no native comparison',input_raw_sha256=hashlib.sha256(raw).hexdigest(),fixture='Synthetic XTAL board frequency24MHz, mode0, clean ownership, inactive controller; optional second user0',comparisons=rows,limits=['Software user bitmap retention is proved in these fixtures; naturally occurring hardware defect/leak is not.','Repeated requests use a bit, not a reference counter.','Counters/delay loop are original software execution; physical startup and ISR interleaving not modeled.']),indent=2)+'\n');print('PASS',len(rows),'original lifetime sequences')

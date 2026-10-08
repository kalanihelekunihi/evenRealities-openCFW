from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0])
from startup_evidence import initialized_record
initialized=initialized_record(raw);targets=set(v&~1 for v in struct.unpack_from('<27I',initialized,0x2a8));cuts=targets-{0x5a40b0,0x5a40b2,0x5a40b4}
def run(entry,a,old_a,b,old_b):
 u=machine();u.mem_write(0x20000000,bytes(initialized));boundary=[];select=[]
 def hook(u,pc,n,d):
  if pc in [0x5a4334,sym['audio_platform_select']&~1]:select.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
  if pc in cuts or pc==0x5a423c:boundary.append(dict(address=hex(pc),arguments=[u.reg_read(r) for r in ([UC_ARM_REG_R0,UC_ARM_REG_R1] if pc==0x5a423c else [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]) ]));u.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[a,old_a,b,old_b]):u.reg_write(r,v)
 u.emu_start(entry|1,0x2007f000,count=100000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
 if a==old_a and b==old_b:assert not boundary and not select
 return dict(boundary=boundary,selector_calls=select,initialized_data_sha256=hashlib.sha256(u.mem_read(0x20000000,len(initialized))).hexdigest())
rows=[]
for kind,a,old_a,b,old_b in itertools.product(['apply','step'],range(20),range(20),[0,7],[0,7]):
 original=0x5a453c if kind=='apply' else 0x5a44ba;native=sym['audio_platform_apply'] if kind=='apply' else sym['audio_platform_step'];o=run(original,a,old_a,b,old_b);n=run(native,a,old_a,b,old_b);assert o==n,(kind,a,old_a,b,old_b,o,n);rows.append(dict(kind=kind,next_a=a,old_a=old_a,next_b=b,old_b=old_b,**o))
(D/'route-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Independent routing and selector wrappers with authenticated initial pointer table/data; helpers use original target child functions.','Nontrivial transition/voltage children stop at first instruction; real BX-LR children24/25/26 execute without substitution.','No completed hardware transition, later pointer mutation, calibration or physical settling simulated.']),indent=2)+'\n');print('PASS',len(rows),'apply/step routing comparisons')

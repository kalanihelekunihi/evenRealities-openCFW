from pathlib import Path
import itertools,json,hashlib,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
def run(native,shadow=1,powered=1,fail_call=0,valid=0,pattern=0,mask=0):
 u=machine();w(u,0x400201bc,shadow<<3);w(u,0x40021008,powered<<27);u.mem_write(0x20071948,b'\xa5'*128);w(u,0x20071948,valid);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 for base,size,salt in [(0x42002000,8192,0x13570000),(0x42006000,16384,0x24680000)]:u.mem_write(base,struct.pack('<'+'I'*(size//4),*[(salt+i)^pattern for i in range(size//4)]))
 calls=[];writes=[];events=[]
 def code(u,a,n,d):
  if a==0x4d3f3c:
   calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)])
   if fail_call and len(calls)==fail_call:w(u,0x40021008,0);events.append(['synthetic_otp_unavailable_before_read',fail_call])
 def write(u,ac,a,n,v,d):writes.append([a,n,v&((1<<(n*8))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x20071948,end=0x200719c7)
 u.emu_start((sym['audio_info1_populate'] if native else 0x47f954)|1,0x2007f000,count=100000)
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 return dict(status=u.reg_read(UC_ARM_REG_R0),calls=calls,writes=writes,events=events,cache=bytes(u.mem_read(0x20071948,128)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for shadow,powered,valid,pattern,mask in itertools.product([0,1],[0,1],[0,0x1f01600d],[0,0xffffffff],[0,1]):
 case=dict(shadow=shadow,powered=powered,valid=valid,pattern=pattern,mask=mask);o=run(False,**case);n=run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
for fail_call,valid,pattern,mask in itertools.product(range(2,10),[0,0x1f01600d],[0,0xffffffff],[0,1]):
 case=dict(fail_call=fail_call,valid=valid,pattern=pattern,mask=mask);o=run(False,**case);n=run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
(D/'info-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Actual stock INFO1 provider, no successful-return or failure-return stubs.','Synthetic INFO1 words and OTP availability drop before selected read; not factory calibration or observed hardware faults.','First MRAM read failure branch is statically reconstructed but not artificially forced.']),separators=(',',':'))+'\n');print('PASS',len(rows),'INFO1 comparisons')

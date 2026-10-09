from pathlib import Path
import itertools,json
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
def run(native,requested=0,current=0,active=0,flag=0,explicit=0,lshz=32768,mask=0):
 u=machine();u.mem_write(0x20073324,b'\0'*56);w(u,0x20073344,active);w(u,0x200001d8,lshz);w(u,0x20074250,current);u.mem_write(0x20074f57,bytes([flag]));w(u,0x20074264,0x20006100);u.mem_write(0x20004536,b'\0');u.mem_write(0x20073f30,b'\xa5'*12)
 for i,v in enumerate([0xabcdef00,0x12345678,0xffffffff]):w(u,0x20006000+4*i,v)
 u.reg_write(UC_ARM_REG_R0,requested);u.reg_write(UC_ARM_REG_R1,0x20006000 if explicit else 0);u.reg_write(UC_ARM_REG_PRIMASK,mask);writes=[];calls=[]
 def wr(u,ac,a,n,v,d):writes.append([a,n,v])
 def code(u,a,n,d):
  if a in [0x4d3914,0x4d3938,0x4d3944]:
   calls.append(dict(address=hex(a),args=[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)] if a==0x4d3914 else [u.reg_read(UC_ARM_REG_R0)] if a==0x4d3938 else []))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40020000,end=0x40021fff);u.emu_start((sym['audio_hfrc_config'] if native else 0x4c38a0)|1,0x2007f000,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 return dict(status=u.reg_read(UC_ARM_REG_R0),writes=writes,calls=calls,config=bytes(u.mem_read(0x20073f30,12)).hex(),selected=word(u,0x20074250),valid=bytes(u.mem_read(0x20004536,1)).hex(),stabilizing=bytes(u.mem_read(0x20074f57,1)).hex(),pointer=word(u,0x20074264),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for requested,current,active,flag,explicit,lshz,mask in itertools.product([0,48000000,123],[0,48000000,123],[0,1],[0,1],[0,1],[0,32768,48000000],[0,1]):
 case=dict(requested=requested,current=current,active=active,flag=flag,explicit=explicit,lshz=lshz,mask=mask);o=run(False,**case);n=run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
(D/'hfrc-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Actual target/apply/disable providers execute with no status-return stubs.','Stock target/apply bodies always return0 for nonzero reference fixture; nonzero provider error rollback branch is static only.','Software config valid does not prove HFRC physical frequency or closed-loop convergence.']),separators=(',',':'))+'\n');print('PASS',len(rows),'HFRC configuration comparisons')

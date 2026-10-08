from pathlib import Path
import json,hashlib,itertools
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
rows=[]
for previous_status,mask in itertools.product([0,1,4,9,0xffffffff],[0,1]):
 u=machine();w(u,0x40021108,3<<4);u.reg_write(UC_ARM_REG_R0,previous_status);u.reg_write(UC_ARM_REG_PRIMASK,mask);calls=[]
 def code(u,a,n,d):
  if a==0x47fea0:calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x4c2af5,0x4c2afc,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x4c2afc;assert calls==[[0,0]];assert u.reg_read(UC_ARM_REG_R0)==0
 rows.append(dict(previous_status=previous_status,mask=mask,calls=calls,status_after_power_control=u.reg_read(UC_ARM_REG_R0),primask=u.reg_read(UC_ARM_REG_PRIMASK)))
(D/'caller-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Original instruction block0x4C2AF4..0x4C2AFC only, actual power-control provider executes with buck-already-active fixture.','Prior initializer result is injected at its continuation; not complete platform/board initialization validation.']),indent=2)+'\n');print('PASS',len(rows),'platform error-discard comparisons')

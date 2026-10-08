from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0])
rows=[]
for next_,old in itertools.product(range(20),range(20)):
 vals=[]
 for entry in [0x5a4334,sym['audio_platform_select']]:
  u=machine();u.mem_write(0x20006000,b'\xa5'*8);u.reg_write(UC_ARM_REG_R0,next_);u.reg_write(UC_ARM_REG_R1,old);u.reg_write(UC_ARM_REG_R2,0x20006003);u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;after=bytes(u.mem_read(0x20006000,8));assert after[:3]+after[4:]==b'\xa5'*7;v=u.reg_read(UC_ARM_REG_R0);assert v in [0,7] and after[3]<=26;assert (v==7)==(after[3]==26);vals.append((v,after[3]))
 assert vals[0]==vals[1],(next_,old,vals);rows.append(dict(next=next_,old=old,result=vals[0][0],transition_index=vals[0][1]))
(D/'select-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Exhaustive selected profile-domain0..19 pairs; no out-of-domain stack-index behavior claim.','Transition index/data selection is not execution or hardware effect of target children.']),indent=2)+'\n');print('PASS',len(rows),'transition selector comparisons')

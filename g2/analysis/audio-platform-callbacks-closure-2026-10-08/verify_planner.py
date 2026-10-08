from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0])
rows=[]
for initial,range_,state,request,masks,power in itertools.product([0,1,0xa5a5a5a5],[0,1,2,3,4,15],[0,1,2,3],[0,1,2,3],[(0,0),(1,0),(0xc0000000,0),(0xc00000,0),(0,0x4c4)],[0,2]):
 vals=[]
 for entry in [0x5a45d0,sym['audio_platform_plan']]:
  u=machine();w(u,0x200742b0,initial);w(u,0x40021000,power);u.mem_write(0x20006000,struct.pack('<4I3B',*masks,0x12345678,0x87654321,range_,state,request));w(u,0x20006100,0xa5a5a5a5);w(u,0x20006104,0xa5a5a5a5)
  for reg,v in [(UC_ARM_REG_R0,0x20006000),(UC_ARM_REG_R1,0x20006100),(UC_ARM_REG_R2,0x20006104)]:u.reg_write(reg,v)
  u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;vals.append((u.reg_read(UC_ARM_REG_R0),word(u,0x20006100),word(u,0x20006104)))
 assert vals[0]==vals[1],(initial,range_,state,request,masks,power,vals);rows.append(dict(initial=hex(initial),range=range_,state=state,request=request,masks=[hex(x) for x in masks],power=power,result=vals[0][0],first=hex(vals[0][1]),second=hex(vals[0][2])))
flags=[]
for next_,old,initial in itertools.product([0,1,2,3,256,258],[0,1,2,257],[0,0xa5]):
 vals=[]
 for entry in [0x5a421c,sym['audio_platform_change_state']]:
  u=machine();u.mem_write(0x20074f68,b'\xa5'*8);u.mem_write(0x20074f6b,bytes([initial]));u.reg_write(UC_ARM_REG_R0,next_);u.reg_write(UC_ARM_REG_R1,old);u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;after=bytes(u.mem_read(0x20074f68,8));assert after[3]==(1 if next_&255==2 and old&255==1 else initial);assert after[:3]+after[4:]==b'\xa5'*7;vals.append(after.hex())
 assert vals[0]==vals[1];flags.append(dict(next=next_,old=old,initial=initial,after=vals[0]))
(D/'planner-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows)+len(flags),plan_cases=len(rows),state_flag_cases=len(flags),plan_comparisons=rows,state_flag_comparisons=flags,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Independent integer planner and state flag setter, actual selected instructions complete; synthetic register/feature inputs.','Planning result is a profile selection, not a physical power/DMA state.','Invalid first/second key can return5 after only partial output publication; matches original.']),indent=2)+'\n');print('PASS',len(rows),len(flags),'planner/state comparisons')

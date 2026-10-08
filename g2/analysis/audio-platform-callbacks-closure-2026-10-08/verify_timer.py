from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0])
from itcm_record import decode_itcm
itcm=decode_itcm(raw);rows=[]
for kind,delay,initial,allowed,mask in itertools.product(['initialize','start','restart'],[0,1,5,50,0xffffffff],[0,0xa5a5a5a5],[0,1],[0,1]):
 vals=[]
 for entry in [{'initialize':0x4801fc,'start':0x480240,'restart':0x48028a}[kind],sym['audio_spot_timer_'+kind]]:
  u=machine();u.mem_map(0,0x1000);u.mem_write(0x40,itcm);u.mem_map(0x40008000,0x1000);u.mem_map(0x40004000,0x1000);u.mem_map(0xe000e000,0x2000);w(u,0x400204e8,0x140);u.mem_write(0x20004536,bytes([allowed]));u.reg_write(UC_ARM_REG_PRIMASK,mask)
  for a in [0x400083e0,0x400083f0,0x400083e8,0x400083ec,0x40008068,0x40008060,0x40008010]:w(u,a,initial)
  writes=[];calls=[]
  def write(u,access,a,n,v,d):writes.append([hex(a),n,v])
  def hook(u,a,n,d):
   if a==0x4c44bc:calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
  u.hook_add(UC_HOOK_CODE,hook)
  for begin,end in [(0x40008000,0x40008fff),(0xe000e108,0xe000e10b),(0xe000e288,0xe000e28b)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=begin,end=end)
  u.reg_write(UC_ARM_REG_R0,delay);u.emu_start(entry|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_PRIMASK)==mask
  if kind=='initialize':expected=[['0x400083e0',4,initial&~1],['0x400083e0',4,0x110],['0x400083f0',4,0x100],['0x400083e8',4,0xffffffff],['0x400083ec',4,0xffffffff],['0x40008068',4,0xc0000000],['0x40008060',4,initial|0x40000000]]
  elif kind=='start':expected=[['0x400083e8',4,(delay*6)&0xffffffff],['0x40008010',4,initial|0x8000],['0x400083e0',4,initial|2],['0x400083e0',4,initial&~2],['0xe000e108',4,0x40000],['0x400083e0',4,(initial&~2)|1]]
  else:expected=[['0x400083e0',4,initial&~1],['0x400083e0',4,(initial&~1)|2],['0x400083e0',4,initial&~3],['0x400083e8',4,(delay*6)&0xffffffff],['0x40008068',4,0xc0000000],['0xe000e288',4,0x40000],['0x400083e0',4,(initial&~3)|1]]
  assert writes==expected,(kind,writes,expected);assert calls==([[4,49]] if kind=='start' else []);vals.append(dict(writes=writes,clock_calls=calls,clock_state=bytes(u.mem_read(0x20073324,56)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK)))
 assert vals[0]==vals[1];rows.append(dict(kind=kind,microseconds=delay,initial=hex(initial),clock_allowed=allowed,initial_primask=mask,**vals[0]))
(D/'timer-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Independent wrappers with common actual clock acquisition; passive synthetic timer/NVIC MMIO.','Intended microsecond units and6MHz factor corroborated by pinned HAL; real clock frequency/timer IRQ delivery not measured.','Start discards clock-request return in source; no forced success stubs and no live clock-failure claim.','No hardware IRQ/exception return or boost-completion scheduling.']),indent=2)+'\n');print('PASS',len(rows),'timer initialize/start/restart comparisons')

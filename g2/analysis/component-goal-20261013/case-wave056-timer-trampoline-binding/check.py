from pathlib import Path
import json,struct,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];B=H.parent
F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';raw=F.read_bytes()[32:];E=B/'case-wave039-list-cursor-contract/final/case.elf'
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
callbacks=[(0x9d70,'case_boot_transport_cb_9d70'),(0xbb4c,'case_boot_transport_cb_bb4c'),(0x9684,'case_boot_transport_cb_9684'),(0xb7ec,'case_boot_transport_cb_b7ec'),(0xbb90,'case_boot_transport_cb_bb90'),(0xab70,'case_boot_transport_cb_ab70')]
cat=list(map(json.loads,(R/'g2/research/corpus/case/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines()))
assert not any(int(x['body_start'],16)<=0x8008568<=int(x['body_end_inclusive'],16) for x in cat)
assert struct.unpack_from('<H',raw,0x8568)[0]==0x4788
assert raw[0x8558:0x856c].hex()=='10b502f0a3ff002803d0426801681046884710bd'
# Direct calls decoded from raw Thumb BL halves, excluding no data automatically.
def bl(pc):
 a,b=struct.unpack_from('<HH',raw,pc)
 if a&0xf800!=0xf000 or b&0xd000!=0xd000:return None
 s=(a>>10)&1;j1=(b>>13)&1;j2=(b>>11)&1;imm=(s<<24)|((1^(j1^s))<<23)|((1^(j2^s))<<22)|((a&1023)<<12)|((b&2047)<<1)
 if s:imm-=1<<25
 return 0x8000000+pc+4+imm
calls={hex(t):[hex(0x8000000+p) for p in range(0,len(raw)-3,2) if bl(p)==t] for t in [0x800aa48,0x800ccc0,0x800ccf2,0x800af30]}
assert calls['0x800aa48']==list(map(hex,[0x8006972,0x8006984,0x8006994,0x80069a4,0x80069b4,0x80069c4]))
def run(source,cb,arg,context=True):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x8000000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x2000)
 if source:
  for a,d in segs:u.mem_write(a,d)
  entry=syms['case_boot_transport_entry_8558'];target=syms[cb[1]]&~1
 else:u.mem_write(0x8000000,raw);entry=0x8008559;target=0x8000000+cb[0]
 task=0x200014b8;pair=0x20004000
 u.mem_write(task+28,struct.pack('<I',pair if context else 0));u.mem_write(pair,struct.pack('<II',target|1,arg))
 u.reg_write(UC_ARM_REG_SP,0x20002c88);u.reg_write(UC_ARM_REG_R0,task);u.reg_write(UC_ARM_REG_LR,0x801ff01)
 out={};low=0x20002c88
 def hook(uc,pc,size,data):
  nonlocal low
  low=min(low,uc.reg_read(UC_ARM_REG_SP))
  if pc in (target,0x801ff00):out.update(endpoint='callback' if pc==target else 'return',R0=uc.reg_read(UC_ARM_REG_R0),stack_bytes=0x20002c88-low);uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry,0,count=10000)
 assert out,(source,cb,arg)
 assert out['endpoint']==('callback' if context else 'return')
 if context:assert out['R0']==arg
 return out
rows=[]
for cb in callbacks:
 for arg in [0,1,0x80000000,0xffffffff]:
  n=run(False,cb,arg);s=run(True,cb,arg);rows.append(dict(callback_native=hex(0x8000000+cb[0]),source_symbol=cb[1],argument=hex(arg),native=n,source=s))
rows.append(dict(null_context=True,native=run(False,callbacks[0],0,False),source=run(True,callbacks[0],0,False)))
r=dict(status='PASS_25_REAL_TRAMPOLINE_ENTRY_CUT_PAIRS',catalogue_omission='08008558..0800856b known code absent from400-function catalogue; BLX08008568 omitted by catalogue-limited wave055 scan',direct_raw_BL_candidates=calls,comparisons=rows,limits=['Real context lookup/lock/unlock and trampoline executed; callback entry cuts stop before callback bodies, no fabricated helper providers','Raw BL scan candidates require code/data classification; six AA48 calls authenticated by pinned prior receipt','Seeded valid task/context pairs qualify ABI, not allocation/registration lifetime or hardware execution','No global stack bound, corpus admission or interval promotion'])
(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],calls)

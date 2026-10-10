from pathlib import Path
import hashlib,struct,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent
root=D.parents[2]
raw=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
with (D/'candidate.elf').open('rb') as f:
 e=ELFFile(f); sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS']; sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
def word(a): return struct.unpack('<I',raw[a-0x437fe0:a-0x437fe0+4])[0]
literals=[word(x) for x in [0x5412c8,0x541268,0x541264,0x5412d0,0x5412cc,0x5412d4]]+[0]
callbacks={0x4490cc:'g2_flashdb_candidate_tick',0x54454a:'g2_flashdb_candidate_get_blob',0x43d0ce:'g2_flashdb_candidate_flags',0x43d574:'g2_flashdb_candidate_log',0x43ce9e:'g2_flashdb_candidate_compress'}
results=[]
for index,size,plen,flags in [(0,0,0,0),(1,4,8,0),(0x101,0x10003,8,0),(255,0xffff,32,0),(2,10,0,1),(3,10,0,2),(4,10,0,4),(5,10,0,7)]:
 outputs=[]
 for stock in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x100000,0x10000);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000)
  for a,b in sections:u.mem_write(a,b)
  u.mem_write(sym['g2_flashdb_candidate_literals'],struct.pack('<7I',*literals))
  u.mem_write(sym['flag_value'],struct.pack('<I',flags));u.mem_write(sym['payload_len'],struct.pack('<I',plen));u.mem_write(sym['payload'],bytes(range(32)))
  u.mem_write(0x20080000,b'key\0');u.mem_write(0x20081000,b'\xcc'*64)
  for r,v in [(UC_ARM_REG_R0,index),(UC_ARM_REG_R1,0x20080000),(UC_ARM_REG_R2,0x20081000),(UC_ARM_REG_R3,size),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x108001)]:u.reg_write(r,v)
  def hook(u,a,n,d):
   if a==0x108000:u.emu_stop()
   elif a in callbacks:u.reg_write(UC_ARM_REG_PC,sym[callbacks[a]])
   elif not (0x100000<=a<0x108000 or (stock and 0x54116e<=a<0x5411f2)):raise RuntimeError(hex(a))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x54116f if stock else sym['g2_flashdb_candidate_blob_read']),0,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x108000 and u.reg_read(UC_ARM_REG_SP)==0x200ff000
  count=struct.unpack('<I',u.mem_read(sym['used'],4))[0]
  outputs.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20081000,64)).hex(),bytes(u.mem_read(sym['trace'],count*4)).hex()))
 assert outputs[0]==outputs[1]
 results.append(dict(index=index,length=size,payload_len=plen,flags=flags,return_value=outputs[0][0],pass_=True))
(D/'verification.json').write_text(json.dumps(dict(count=len(results),all_pass=True,callbacks='same executable C callbacks for stock and candidate',cases=results),indent=2)+'\n')
print('PASS:',len(results),'stock vs source wrapper runs with C copy/log/tick callbacks')

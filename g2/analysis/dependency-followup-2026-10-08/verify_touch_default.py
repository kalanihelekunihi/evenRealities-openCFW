"""Exercise new source-compiled default-fill APIs against stock instructions."""
from pathlib import Path
import json,hashlib,struct,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';image=fw[32:];elfpath=Path(sys.argv[1])
with elfpath.open('rb') as f:
 e=ELFFile(f);s=e.get_section_by_name('.text');text=s.data();assert s['sh_addr']==0x9218 and text==image[0x5f18:0x6016]
def run(native,checked,ctrl,status,count,value):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x3000,0x9000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40250000,0x1000)
 u.mem_write(0x9218,text) if native else u.mem_write(0x3300,image)
 u.mem_write(0x40250000,struct.pack('<I',ctrl));u.mem_write(0x40250208,struct.pack('<I',status));u.reg_write(UC_ARM_REG_R0,0x40250000);u.reg_write(UC_ARM_REG_R1,value);u.reg_write(UC_ARM_REG_R2,count);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);events=[]
 def hook(u,access,addr,size,value,user):
  if 0x40250000<=addr<0x40251000:events.append(['read' if access==16 else 'write',addr,size,value if access!=16 else int.from_bytes(u.mem_read(addr,size),'little')])
 u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,hook);u.emu_start((0x92e6 if checked else 0x92d6)|1,0x20000000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 result=dict(events=events,sp=u.reg_read(UC_ARM_REG_SP));
 if checked:result['return']=u.reg_read(UC_ARM_REG_R0)
 return result
cases=[]
for checked in [False,True]:
 for ctrl in ([0] if not checked else [0,0x4000,0x8000,0xc000]):
  depth=8 if ctrl&0xc000 else 16
  for status in ([0] if not checked else [0,3,depth,0xffff0003]):
   for count in [0,1,5,17]:
    for value in [0x12345678,0xffffffff]:
     x=run(False,checked,ctrl,status,count,value);y=run(True,checked,ctrl,status,count,value);assert x==y
     expected=min(count,depth-(status&511)) if checked else count;writes=[i for i in y['events'] if i[0]=='write'];assert writes==[['write',0x40250240,4,value]]*expected
     if checked:assert y['return']==expected
     cases.append(dict(checked=checked,ctrl=ctrl,status=status,count=count,value=value,result=y))
r=dict(status='PASS_TOUCH_DEFAULT_SOURCE',cases=len(cases),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),comparisons=cases,limits=['Actual stock and public-source-compiled bodies/callees execute without child stubs.','FIFO status/config are synthetic RAM; writes are observed, not transmitted on hardware.','Counts are elements; full uint32 data is written without software width truncation. Hardware may apply configured data width.','No malformed occupancy underflow, concurrent consumer, IRQ or physical FIFO timing proof.'])
(D/'touch-default-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'stock/public-source default-fill cases')

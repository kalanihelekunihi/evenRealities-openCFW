"""Compare only slave IRQ dispatch with five explicit void helper cuts."""
from pathlib import Path
import json,hashlib,struct,sys,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';image=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
helpers={'SlaveHandleHsMode':0x9344,'SlaveHandleDataReceive':0x9748,'SlaveHandleStop':0x93c4,'SlaveHandleAddress':0x95b8,'SlaveHandleDataTransmit':0x97fc};stock_pcs=set()
def run(native,wake,slave,rx,accept,tx,room):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40250000,0x1000)
 if native:
  for addr,raw in segments:u.mem_write(addr,raw)
 else:u.mem_write(0x3300,image)
 def setreg(off,v):u.mem_write(0x40250000+off,struct.pack('<I',v))
 def getreg(off):return int.from_bytes(u.mem_read(0x40250000+off,4),'little')
 for off,v in [(0,0x10000 if accept else 0),(0xe8c,wake),(0xf4c,slave),(0xfcc,rx),(0xf8c,tx),(0x308,3),(0xfc8,rx)]:setreg(off,v)
 ctx=bytearray(84);struct.pack_into('<I',ctx,0x3c,room);u.mem_write(0x20002000,bytes(ctx));u.reg_write(UC_ARM_REG_R0,0x40250000);u.reg_write(UC_ARM_REG_R1,0x20002000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);events=[];cuts={((symbols[n] if native else a)&~1):n for n,a in helpers.items()}
 def code(u,pc,size,user):
  if not native and 0x9b0c<=pc<0x9c20:stock_pcs.update(range(pc,pc+size))
  if pc in cuts:
   name=cuts[pc];args=[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]
   if name=='SlaveHandleStop':args.append(u.reg_read(UC_ARM_REG_R2))
   events.append(['helper',name,args]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  if 0x110000<=pc<0x110020:raise AssertionError('Unexpected modeled external child reached')
 def write(u,access,addr,size,value,user):
  if 0x40250000<=addr<0x40251000:
   off=addr-0x40250000;events.append(['write',off,size,value]);assert size==4
   # Explicit synthetic W1C/status model, not observed hardware.
   clear={0xe80:0xe8c,0xf40:0xf4c,0xfc0:0xfcc,0xf80:0xf8c}
   if off in clear:setreg(clear[off],getreg(clear[off])&~value)
   if off==0xfc4:setreg(0xfcc,getreg(0xfcc)|value)
   if off==0xfc8:setreg(0xfcc,getreg(0xfcc)&value)
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((symbols['Cy_SCB_I2C_SlaveInterrupt'] if native else 0x9b0c)|1,0x20000000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return dict(events=events,context=u.mem_read(0x20002000,84).hex(),mmio_sha256=hashlib.sha256(u.mem_read(0x40250000,0x1000)).hexdigest(),sp=u.reg_read(UC_ARM_REG_SP))
cases=[]
for vals in itertools.product([0,1],[0,0x10,0x40,0x80,0xc0,1,0x100,0x101,0x3000000,0x30000c0,0x50,0x90,0xd0,0x110,0x150],[0,1],[False,True],[0,0x41],[0,7]):
 x=run(False,*vals);y=run(True,*vals);assert x==y,(vals,x,y);cases.append(dict(inputs=vals,result=x))
r=dict(status='PASS_BOUNDED_SLAVE_IRQ_DISPATCH',cases=len(cases),original_instruction_bytes_observed=len(stock_pcs),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),stock_body_sha256=hashlib.sha256(image[0x680c:0x6920]).hexdigest(),helper_cuts=helpers,comparisons=cases,limits=['Only actual top-level dispatch instructions execute; five helpers are intercepted at entry and treated as void/no-state-change. No helper implementation or callback ownership claim.','Synthetic W1C/masked-status fixture only; no hardware interrupt timing or actual concurrent event delivery.','Unexecuted delay/division/critical-section external link aliases are guarded; reaching one fails.','Complete context, MMIO digest, ordered writes/consumed helper arguments and SP compare.','Stock276 and public300-byte body differ; bounded dispatch compatibility only, no exact byte attribution.'])
(D/'touch-i2c-irq-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'IRQ dispatch cases;',len(stock_pcs),'stock instruction bytes observed; five explicit child cuts')

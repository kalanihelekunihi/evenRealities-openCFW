"""Compare actual slave IRQ helpers and public critical assembly; null callbacks only."""
from pathlib import Path
import json,hashlib,struct,sys,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';image=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
helpers={'SlaveHandleHsMode':0x9344,'SlaveHandleDataReceive':0x9748,'SlaveHandleStop':0x93c4,'SlaveHandleAddress':0x95b8,'SlaveHandleDataTransmit':0x97fc};stock_pcs=set(); all_stock_pcs=set()
def run(native,wake,slave,rx,accept,tx,room,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40250000,0x1000)
 if native:
  for addr,raw in segments:u.mem_write(addr,raw)
 else:u.mem_write(0x3300,image)
 def setreg(off,v):u.mem_write(0x40250000+off,struct.pack('<I',v))
 def getreg(off):return int.from_bytes(u.mem_read(0x40250000+off,4),'little')
 for off,v in [(0,0x10000 if accept else 0),(0xe8c,wake),(0xf4c,slave),(0xfcc,rx),(0xf8c,tx),(0x308,3),(0xfc8,rx)]:setreg(off,v)
 ctx=bytearray(84);ctx[0]=1;ctx[1]=1;struct.pack_into('<I',ctx,4,0x10000000);struct.pack_into('<I',ctx,0x28,0x20004000);struct.pack_into('<I',ctx,0x2c,room);struct.pack_into('<I',ctx,0x38,0x20003000);struct.pack_into('<I',ctx,0x3c,room);u.mem_write(0x20003000,b'\xcc'*64);u.mem_write(0x20004000,bytes(range(64)));u.reg_write(UC_ARM_REG_PRIMASK,mask);u.mem_write(0x20002000,bytes(ctx));u.reg_write(UC_ARM_REG_R0,0x40250000);u.reg_write(UC_ARM_REG_R1,0x20002000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);events=[];cuts={((symbols[n] if native else a)&~1):n for n,a in helpers.items()}
 def code(u,pc,size,user):
  if not native and 0x3300<=pc<0x3300+len(image):all_stock_pcs.update(range(pc,pc+size))
  if not native and 0x9b0c<=pc<0x9c20:stock_pcs.update(range(pc,pc+size))
  if pc in cuts:
   name=cuts[pc];args=[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]
   if name=='SlaveHandleStop':args.append(u.reg_read(UC_ARM_REG_R2))
   events.append(['helper-enter',name,args])
  if 0x110000<=pc<0x110020:raise AssertionError('Unexpected modeled external child reached')
 def write(u,access,addr,size,value,user):
  if 0x40250000<=addr<0x40251000:
   off=addr-0x40250000;events.append(['write',off,size,value]);assert size==4
   # Explicit synthetic W1C/status model, not observed hardware.
   clear={0xe80:0xe8c,0xf40:0xf4c,0xfc0:0xfcc,0xf80:0xf8c}
   if off in clear:setreg(clear[off],getreg(clear[off])&~value)
   if off==0xfc4:setreg(0xfcc,getreg(0xfcc)|value)
   if off==0xfc8:setreg(0xfcc,getreg(0xfcc)&value)
   if off==0x240:setreg(0x208,getreg(0x208)+1)
 fifo=[0x0c,0x34,0x56]
 def read(u,access,addr,size,value,user):
  if addr==0x40250340:
   v=fifo.pop(0) if fifo else 0;setreg(0x340,v);setreg(0x308,len(fifo));events.append(['fifo-pop',v])
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((symbols['Cy_SCB_I2C_SlaveInterrupt'] if native else 0x9b0c)|1,0x20000000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return dict(events=events,context=u.mem_read(0x20002000,84).hex(),mmio_sha256=hashlib.sha256(u.mem_read(0x40250000,0x1000)).hexdigest(),sp=u.reg_read(UC_ARM_REG_SP),primask=u.reg_read(UC_ARM_REG_PRIMASK),rx_buffer=u.mem_read(0x20003000,64).hex(),tx_buffer=u.mem_read(0x20004000,64).hex())
cases=[]
for vals in itertools.product([0,1],[0,0x10,0x40,0xc0,1,0x100,0x101,0x30000c0],[0,1],[False,True],[0,0x41],[0,7],[0,1]):
 x=run(False,*vals);y=run(True,*vals);assert x==y,(vals,x,y);cases.append(dict(inputs=vals,result=x))
r=dict(status='PASS_BOUNDED_REAL_SLAVE_HELPERS',cases=len(cases),original_instruction_bytes_observed=len(stock_pcs),all_reached_original_instruction_bytes=len(all_stock_pcs),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),stock_body_sha256=hashlib.sha256(image[0x680c:0x6920]).hexdigest(),helper_entries_observed=helpers,comparisons=cases,limits=['Actual stock/public top-level and reached five helper bodies execute, including real public critical-section assembly; helper entries are observed without interception.',
'Synthetic W1C/status and three-value FIFO; null callbacks only. No real event timing, callback reentrancy or IRQ concurrency.',
'Context, both64-byte guarded buffers, MMIO digest, ordered writes/consumed helper arguments, SP and PRIMASK compare.',
'Any unexpected modeled external alias fails; source ELF contains no numeric executable aliases or stock code.',
'No exact-body attribution beyond the six FIFO functions or production build claim.'])
(D/'touch-i2c-real-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'actual-helper IRQ cases;',len(stock_pcs),'top-level stock instruction bytes observed; no helper cuts')

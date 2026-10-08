from pathlib import Path
import json,hashlib,struct,sys,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';image=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
def run(native,events,count,op,value,n1,n2):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40250000,0x1000);u.mem_map(0x40040000,0x1000)
 if native:
  for addr,raw in segments:u.mem_write(addr,raw)
 else:u.mem_write(0x3300,image)
 ctx=bytearray(b'\xcc'*96);struct.pack_into('<I',ctx,64,count);u.mem_write(0x200008ec,bytes(ctx));u.mem_write(0x20000998,b'\xdd'*48);u.mem_write(0x200009a0,bytes([op,value&255,value>>8])+bytes(range(3,16)));u.mem_write(0x200009b0,bytes(range(0xa0,0xb0)));u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_R0,events);writes=[];cut=[]
 u.mem_write(0x200009c8,b'\x99'*32);u.mem_write(0x200009d4,struct.pack('<HH',0x1234,0xabcd));u.mem_write(0x200004e8,struct.pack('<H',0x5678));u.mem_write(0x200004ec+12,struct.pack('<I',0x20002000))
 for widget,n,addr in [(1,n1,0x20003000),(2,n2,0x20004000)]:
  u.mem_write(0x20002000+widget*0x90+4,struct.pack('<I',addr));u.mem_write(0x20002000+widget*0x90+0x38,struct.pack('<H',n))
  for i in range(n):u.mem_write(addr+i*10+4,struct.pack('<H',0x1100+widget*16+i))
 def code(u,pc,size,user):
  if pc==((symbols['touch_reset_boundary']&~1) if native else 0x7e14):cut.append('reset-entry');u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code)
 def write(u,access,addr,size,value,user):
  if addr==0x40040440:writes.append([addr,size,value])
 u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((symbols['app_event'] if native else 0x3700)|1,0x20000000,count=6000);assert bool(cut) or u.reg_read(UC_ARM_REG_PC)==0x20000000;assert int.from_bytes(u.mem_read(0x20007000,4),'little')==0
 return dict(context=u.mem_read(0x200008ec,96).hex(),buffers_and_guards=u.mem_read(0x20000998,48).hex(),mmio_writes=writes,sp=None if cut else u.reg_read(UC_ARM_REG_SP),configuration=u.mem_read(0x200009c8,32).hex(),threshold=u.mem_read(0x200004e8,2).hex(),mailbox=u.mem_read(0x20000000,1).hex(),cut=cut)
cases=[]
for v in itertools.product([0,1,2,4,8,0x10,0x20,0x30,0x40,0x60,0x70,0xffffffff],[0,1,16,17,255,256,257],range(10),[0,1,0x1234,0xffff],[0,4],[0,1]):
 x=run(False,*v);y=run(True,*v);assert x==y,(v,x,y);cases.append(dict(inputs=v,result=x))
report=dict(status='PASS_BOUNDED_ALL_COMMAND_BRANCHES',cases=len(cases),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),source_sha256=hashlib.sha256((D/'app_event.c').read_bytes()).hexdigest(),comparisons=cases,limits=['Real stock callback/getter/descriptor arms/memset execute; native independent callback calls public descriptor-arm bodies. No child stubs.','Commands0..9, four payload values and synthetic sensor counts widget1 0/4 and widget2 0/1; larger counts outside bounded reconstruction contract.','Raw RX-index257 demonstrates uint8 cast; no actual driver count overflow inferred.','Context,16-byte buffers/guards, MMIO writes and final SP compare; void return/flags and scratch stack are outside contract.','Stock logger executes its actual return-zero leaf; reconstructed code omits its no-state-effect call. Actual sensor helper and memcpy execute. DFU mailbox byte is compared, reset entry is an explicit stop before reset body, no reset/hardware writes.'])
(D/'app-event-results.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(cases),'registered callback stock/source cases')

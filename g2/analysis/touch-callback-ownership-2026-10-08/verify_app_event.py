from pathlib import Path
import json,hashlib,struct,sys,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';image=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
def run(native,events,count,op):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40250000,0x1000);u.mem_map(0x40040000,0x1000)
 if native:
  for addr,raw in segments:u.mem_write(addr,raw)
 else:u.mem_write(0x3300,image)
 ctx=bytearray(b'\xcc'*96);struct.pack_into('<I',ctx,64,count);u.mem_write(0x200008ec,bytes(ctx));u.mem_write(0x20000998,b'\xdd'*48);u.mem_write(0x200009a0,bytes([op])+bytes(range(1,16)));u.mem_write(0x200009b0,bytes(range(0xa0,0xb0)));u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_R0,events);writes=[]
 def write(u,access,addr,size,value,user):
  if addr==0x40040440:writes.append([addr,size,value])
 u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((symbols['app_event'] if native else 0x3700)|1,0x20000000,count=6000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;assert int.from_bytes(u.mem_read(0x20007000,4),'little')==0
 return dict(context=u.mem_read(0x200008ec,96).hex(),buffers_and_guards=u.mem_read(0x20000998,48).hex(),mmio_writes=writes,sp=u.reg_read(UC_ARM_REG_SP))
cases=[]
for v in itertools.product([0,1,2,4,8,0x10,0x20,0x30,0x40,0x60,0x70,0xffffffff],[0,1,16,17,255,256,257],[0,1,3,9]):
 x=run(False,*v);y=run(True,*v);assert x==y,(v,x,y);cases.append(dict(inputs=v,result=x))
report=dict(status='PASS_BOUNDED_REGISTERED_APP_EVENT',cases=len(cases),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),source_sha256=hashlib.sha256((D/'app_event.c').read_bytes()).hexdigest(),comparisons=cases,limits=['Real stock callback/getter/descriptor arms/memset execute; native independent callback calls public descriptor-arm bodies. No child stubs.','Only commands0,1,3,9 tested; other valid command handlers deliberately outside reconstructed callback precondition.','Raw RX-index257 demonstrates uint8 cast; no actual driver count overflow inferred.','Context,16-byte buffers/guards, MMIO writes and final SP compare; void return/flags and scratch stack are outside contract.','Synthetic RAM/register state; no IRQ concurrency, physical I2C traffic, EEPROM/DFU or device writes.'])
(D/'app-event-results.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(cases),'registered callback stock/source cases')

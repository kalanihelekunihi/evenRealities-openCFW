"""Bounded stock/public-source I2C init comparison, no children stubbed."""
from pathlib import Path
import json,hashlib,struct,sys,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';image=fw[32:];elfpath=Path(sys.argv[1])
with elfpath.open('rb') as f:
 e=ELFFile(f);s=e.get_section_by_name('.text');text=s.data();assert s['sh_addr']==0x100000

def run(native,config,nullarg):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x1000);u.mem_map(0x20000000,0x10000);u.mem_map(0x40250000,0x1000)
 u.mem_write(0x100000,text) if native else u.mem_write(0x3300,image)
 u.mem_write(0x40250000,b'\xa5'*0x1000);u.mem_write(0x20001000,config+b'\x55'*8);u.mem_write(0x20002000,b'\xcc'*96)
 for r,v in [(UC_ARM_REG_R0,0x40250000),(UC_ARM_REG_R1,0x20001000),(UC_ARM_REG_R2,0x20002000)]:u.reg_write(r,v)
 if nullarg is not None:u.reg_write([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2][nullarg],0)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);writes=[];reads=[]
 def read(u,access,addr,size,value,user):
  if 0x20001000<=addr<0x20001020:reads.append([addr-0x20001000,size])
 def write(u,access,addr,size,value,user):
  if 0x40250000<=addr<0x40251000:writes.append([addr-0x40250000,size,value])
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((0x100000 if native else 0x98f4)|1,0x20000000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return dict(result=dict(mmio=bytes(u.mem_read(0x40250000,0x1000)).hex(),context=bytes(u.mem_read(0x20002000,96)).hex(),writes=writes,return_value=u.reg_read(UC_ARM_REG_R0),sp=u.reg_read(UC_ARM_REG_SP)),config_reads=reads)
cases=[]
for mode,profile,phase in itertools.product([1,2,3],range(4),[1,8,16]):
 b=bytearray(24);b[0]=mode;b[1]=profile&1;b[2]=(profile>>1)&1;b[3]=0x0c;b[4]=0xfe;b[5]=0;b[6]=profile&1;b[7]=(profile>>1)&1;b[8]=profile&1;b[9]=(profile>>1)&1;struct.pack_into('<IIH',b,12,phase,phase,0x1234)
 x=run(False,bytes(b),None);y=run(True,bytes(b),None);assert x['result']==y['result'],(mode,profile,phase,x,y);cases.append(dict(mode=mode,profile=profile,phase=phase,comparison=x,source_reads=y['config_reads']))
for nullarg in [0,1,2]:
 x=run(False,bytes(b),nullarg);y=run(True,bytes(b),nullarg);assert x['result']==y['result'];cases.append(dict(null_argument=nullarg,comparison=x,source_reads=y['config_reads']))
r=dict(status='PASS_BOUNDED_PUBLIC_I2C_INIT',cases=len(cases),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),source_extent=len(text),stock_extent=438,stock_body_sha256=hashlib.sha256(image[0x65f4:0x67aa]).hexdigest(),comparisons=cases,limits=['Public source compiled GCC13.3 -Og -fshort-enums; equivalent bounded outputs do not establish stock version/compiler or exact bytes.','Actual stock and public-source instructions run, no child stubs; MMIO synthetic RAM.','Ordered MMIO writes, complete96-byte guarded context and peripheral state, return and SP compare. Config read order is recorded but not required equal.','Valid mode1/2/3 and selected flags, phase1/8/16 plus null cases; assertion trap cases, IRQ concurrency, live disabled-state requirement and bus traffic not tested.'])
(D/'touch-i2c-init-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'stock/public-source I2C init cases')

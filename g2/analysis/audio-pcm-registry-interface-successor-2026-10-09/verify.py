from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'g2/analysis/audio-platform-callbacks-closure-2026-10-08'));from itcm_record import decode_itcm
from startup_evidence import initialized_record
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];itcm=decode_itcm(raw);startup=initialized_record(raw);receipt=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(receipt['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
rows=[]
def encode(year,month,day,revision,reserved=0):return ((year&31)<<25)|((month&15)<<21)|((day&31)<<16)|(revision&65535)|((reserved&3)<<30)
def run(native,major,version,date,old=0xa5,action=None,gate=3,cache_enabled=1,gpu=1,range_value=0,state=1):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0,0x1000),(0x40020000,0x2000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw);u.mem_write(0x20000000,bytes(startup));u.mem_write(0x40,itcm)
 for a,b in segments:u.mem_write(a,b)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 w(0xe000ed88,0xf00000);w(0x4002000c,major);w(0x200001e8,version);w(0x2007198c,date);u.mem_write(0x20074f6e,bytes([old])*3);u.mem_write(0x20074f63,bytes([cache_enabled]));w(0x40021108,gate<<4);w(0x40021004,0x40000 if gpu else 0);w(0x20074270,112)
 for a in [0x40020044,0x4002004c]:w(a,0x76543200|112)
 w(0x40020080,0xa5a5a400|1012);w(0x40020088,0xabcdefc0|63)
 for a in [0x40020374,0x40020380,0x40020344,0x4002034c,0x40020354,0x40020358,0x400201b0,0x40021100]:w(a,0x87654321)
 w(0x40021000,0);u.reg_write(UC_ARM_REG_FPSCR,0);reads=[];writes=[];source_instructions=[]
 def hook(u,a,n,d):
  if native:assert 0x100000<=a<0x110000,('source code escaped',hex(a));source_instructions.append(a)
 def rd(u,access,a,n,v,d):
  if a in [0x4002000c,0x200001e8,0x2007198c]:reads.append([hex(a),n,bytes(u.mem_read(a,n)).hex()])
 def wr(u,access,a,n,v,d):
  if 0x40020000<=a<0x40022000:writes.append([hex(a),n,v])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr)
 def invoke(at,arg=0):
  u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);pc=at|1
  for i in range(50000):
   u.emu_start(pc|1,0x2007f000,count=1);pc=u.reg_read(UC_ARM_REG_PC)
   if pc==0x2007f000:return
  raise AssertionError('instruction step budget')
 invoke(sym['pcm_variant_initialize'] if native else 0x5a08e4);assert u.reg_read(UC_ARM_REG_R0)==0 and not writes
 m=major&255;screened=(((date>>25)&31)==24 and ((date>>21)&15)==12 and ((date>>16)&31)>=20 and (date&65535)==0) or (((date>>25)&31)>=25 and (date&65535)==0)
 expected=[int(m==0x21 and version==2),int((m==0x21 and version in [2,3]) or (m==0x22 and version==0)),int((m==0x22 and version==1) or (m==0x23 and version==0 and not screened))]
 assert list(bytes(u.mem_read(0x20074f6e,3)))==expected
 initial_reads=reads.copy()
 if action=='temperature':
  invoke(sym['pcm_hardware_temperature'] if native else 0x5a001c,range_value)
  if gate==3 and cache_enabled:
   boost=15 if gpu and expected[1] else 0;reduce=10 if range_value in [0,1] else 0;assert word(0x4002004c)&127==min(max(112+boost-reduce,0),127)
 elif action=='gpu_on':invoke(sym['pcm_middle_on'] if native else 0x5a0328,state)
 regions=[(0x20074f60,32),(0x2007426c,92),(0x40020000,0x2000)]
 return {'flags':expected,'writes':writes,'state_digest':hashlib.sha256(b''.join(bytes(u.mem_read(a,n)) for a,n in regions)).hexdigest(),'vddf_trim':word(0x4002004c)&127,'memory_trim':word(0x40020088)&63,'primask':u.reg_read(UC_ARM_REG_PRIMASK),'fpscr':u.reg_read(UC_ARM_REG_FPSCR),'source_guard_pass':bool(source_instructions) if native else None}
def compare(c):
 o=run(False,**c);n=run(True,**c);assert n.pop('source_guard_pass');o.pop('source_guard_pass');assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))

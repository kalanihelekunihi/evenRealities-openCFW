from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';im=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
def guest(native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 for a,n in [(0x3000,0x9000),(0x100000,0x20000),(0x20000000,0x10000),(0x40100000,0x1000),(0x40030000,0x1000)]:u.mem_map(a,n)
 if native:
  for a,b in segments:u.mem_write(a,b)
 else:u.mem_write(0x3300,im)
 return u
def checksum(row):
 crc=255
 for v in row[1:len(row)-3]:
  crc^=v
  for j in range(8):crc=((crc<<1)^(0x31 if crc&128 else 0))&255
 return crc
def rows(pattern):
 raw=bytearray(2048)
 for i in range(16):
  r=bytearray(128);seq=[0xfffffffe,0xffffffff,0,1,2,3,4,5][i%8] if pattern=='wrap' else i%8+1
  struct.pack_into('<III',r,4,seq,(i%4)*64+((i%2)*8),[1,16,48][i%3]);r[16:64]=bytes((i*17+j)&255 for j in range(48));r[64:]=bytes((i*29+j)&255 for j in range(64));struct.pack_into('<I',r,0,checksum(r))
  if pattern=='blank':r=bytearray(128)
  elif pattern=='erased':r=bytearray(b'\xff'*128)
  elif pattern=='bad-main' and i<8:r[0]^=1
  elif pattern=='bad-all':r[0]^=1
  elif pattern=='torn-last' and i==7:r[16:48]=b'\x3c'*32
  raw[i*128:(i+1)*128]=r
 return bytes(raw)
def run(native,kind,pattern,redundant,simple,last,sequence,address,length):
 u=guest(native);u.mem_map(0xc000,0x4000);flash=rows(pattern);u.mem_write(0xe400,flash);ctx=bytearray(32);struct.pack_into('<HH',ctx,0,4,128);struct.pack_into('<I',ctx,4,128);struct.pack_into('<I',ctx,8,256);ctx[12]=2;ctx[13]=simple;ctx[14]=redundant;ctx[15]=1;struct.pack_into('<I',ctx,16,0xe400);struct.pack_into('<HH',ctx,20,64,48);struct.pack_into('<I',ctx,24,0xe400+last*128);struct.pack_into('<I',ctx,28,0x20000ed4);u.mem_write(0x200008c8,bytes(ctx));provider=bytearray(48);struct.pack_into('<I',provider,20,symbols['touch_storage_copy'] if native else 0x4861);u.mem_write(0x20000ed4,bytes(provider));scratch=bytearray(b'\xa5'*128);struct.pack_into('<IIII',scratch,0,0,sequence,address,length);scratch[16:64]=bytes((j*7)&255 for j in range(48));u.mem_write(0x20002ff8,b'\xdd'*144);u.mem_write(0x20003000,bytes(scratch));u.mem_write(0x20002000,b'\xcc'*8)
 if kind=='define':args=[0x200008c8];old=0x7fa4;name='touch_define_last'
 elif kind=='integrity':args=[0x20002000,0x200008c8];old=0x8058;name='touch_integrity'
 else:args=[0x20003000,0xe400+last*128,0x200008c8];old=0x814c if kind=='history' else 0x8680;name='touch_history' if kind=='history' else 'touch_merge'
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start((symbols[name] if native else old)|1,0x20000000,count=1000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000,(native,kind,pattern,hex(u.reg_read(UC_ARM_REG_PC)))
 return {'return':u.reg_read(UC_ARM_REG_R0),'context':u.mem_read(0x200008c8,32).hex(),'scratch_guards':u.mem_read(0x20002ff8,144).hex(),'sequence':u.mem_read(0x20002000,8).hex(),'flash_sha256':hashlib.sha256(u.mem_read(0xe400,2048)).hexdigest(),'sp':u.reg_read(UC_ARM_REG_SP)}
patterns=['blank','erased','valid','bad-main','bad-all','torn-last','wrap'];cases=[]
for kind in ['define','integrity','history']:
 for vals in itertools.product(patterns,[0,1],[0,1],[0,3,7]):
  p,r,sm,last=vals;args=(kind,p,r,sm,last,1,0,1);a=run(False,*args);b=run(True,*args);assert a==b,(args,a,b);cases.append({'inputs':args,'result':a})
for vals in itertools.product(patterns,[0,1],[0,7],[0,1,4,0xffffffff],[0,63,64,240],[1,48]):
 p,r,last,seq,addr,length=vals;args=('merge',p,r,0,last,seq,addr,length);a=run(False,*args);b=run(True,*args);assert a==b,(args,a,b);cases.append({'inputs':args,'result':a})
r={'status':'PASS_REAL_INTEGRITY_HISTORY_MERGE_NO_CUTS','cases':len(cases),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'comparisons':cases,'limits':['All actual stock helper/CRC/scan/division/memcpy/copy-callback instructions versus independent native C; no function or SROM cuts in these read-only helper suites.','Rows are synthetic valid/corrupt/blank/erased/torn/wrapped sequences, not captured stock storage.','Coherent128-byte rows,4 logical rows, wear2, bounded payload headers; larger/malformed geometry outside contract.','Flash read-only guest RAM and stable provider table; no physical recovery or concurrent mutation proof.']};(D/'helper-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'real integrity/history/merge cases; no cuts')

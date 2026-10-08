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
source=json.loads((D/'command7-results.json').read_text());cases=[]
def readback(c,application):
 u=guest(False);u.mem_map(0xc000,0x4000);storage=bytes.fromhex(c['result']['storage']);u.mem_write(0xe400,storage);u.mem_write(0x200008c8,bytes.fromhex(c['result']['eeprom_context']));p=bytearray(48)
 for slot,pc in [(5,0x4861),(6,0x4811),(7,0x47b1),(11,0x47ab)]:struct.pack_into('<I',p,slot*4,pc)
 u.mem_write(0x20000ed4,bytes(p));u.mem_write(0x200008c4,b'\x01');u.mem_write(0x20005ff8,b'\xdd'*24)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0,0x20006000,8,0x200008c8]):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start((0x3520 if application else 0x8a78)|1,0x20000000,count=1500000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;assert bytes(u.mem_read(0xe400,2048))==storage
 return {'status':u.reg_read(UC_ARM_REG_R0),'data':u.mem_read(0x20006000,8).hex(),'guards':u.mem_read(0x20005ff8,24).hex()}
for c in source['comparisons']:
 pattern,initialized,simple,mode,param,mask=c['inputs']
 if initialized!=1 or param!=0x1234 or mask!=0:continue
 lib=readback(c,False);app=readback(c,True);assert lib['data']==app['data'];assert app['status']==(0 if lib['status'] in [0,0x093e0004] else 2)
 expected='554e564521433412';cases.append({'inputs':c['inputs'],'ack':c['result']['ack'],'deferred_status':c['result']['application_storage_status'],'library_readback':lib,'application_readback':app,'matches_requested_config':app['data']==expected})
r={'status':'PASS_STOCK_READBACK_AFTER_SYNTHETIC_COMMAND7','cases':len(cases),'comparisons':cases,'limits':['Actual stock read dispatcher/simple or620-byte extended read/checksum/history/provider-copy instructions execute; no cuts.','Readback observes synthetic write-model output, not a physical device or durable storage.','No native-source equivalence is claimed for the620-byte read implementation; this is further original-instruction evidence.','Phone commands6/8 read RAM config, not this persistent-library path; no new on-device readback protocol is implemented.']};(D/'readback-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'actual stock readback cases; native read-source equivalence not claimed')

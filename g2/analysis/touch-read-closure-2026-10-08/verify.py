from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent; ROOT=D.parents[2]; prior=D.parent/'touch-history-closure-2026-10-08'
fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';im=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
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
  elif pattern=='zero-seq-bad':r=bytearray(128);struct.pack_into('<I',r,0,1)
  elif pattern=='bad-main' and i<8:r[0]^=1
  elif pattern=='bad-all':r[0]^=1
  elif pattern=='torn-last' and i==7:r[16:48]=b'\x3c'*32
  raw[i*128:(i+1)*128]=r
 return bytes(raw)
visited=set()
def run(native,storage,context,address,size,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 for a,n in [(0x3000,0x9000),(0xc000,0x4000),(0x100000,0x20000),(0x20000000,0x10000)]:u.mem_map(a,n)
 if native:
  for a,b in segments:u.mem_write(a,b)
 else:u.mem_write(0x3300,im)
 u.mem_write(0xe400,storage);u.mem_write(0x200008c8,context);p=bytearray(48)
 for slot,name,pc in [(5,'touch_storage_copy',0x4861),(6,'touch_storage_program',0x4811),(7,'touch_storage_zero',0x47b1),(11,'touch_storage_no_erase',0x47ab)]:struct.pack_into('<I',p,slot*4,symbols[name] if native else pc)
 u.mem_write(0x20000ed4,bytes(p));u.mem_write(0x20005ff8,b'\xdd'*(size+16))
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[address,0x20006000,size,0x200008c8]):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 if not native:
  def visit(u,pc,n,user):
   if 0x82e0<=pc<0x854c:visited.update(range(pc,pc+n))
  u.hook_add(UC_HOOK_CODE,visit)
 u.emu_start((symbols['touch_eeprom_read'] if native else 0x8a78)|1,0x20000000,count=1500000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 assert bytes(u.mem_read(0xe400,2048))==storage
 return dict(status=u.reg_read(UC_ARM_REG_R0),guards=u.mem_read(0x20005ff8,size+16).hex(),context=u.mem_read(0x200008c8,32).hex(),sp=u.reg_read(UC_ARM_REG_SP),primask=u.reg_read(UC_ARM_REG_PRIMASK))
results=[]
for pattern,simple,wear,red,last,pair in itertools.product(['blank','erased','zero-seq-bad','valid','bad-main','bad-all','torn-last','wrap'],[0,1],[1,2],[0,1],[0,3],[(0,1),(17,48),(63,49),(64,96),(200,48)]):
 address,size=pair;mask=last&1;ctx=bytearray(32);struct.pack_into('<HHII',ctx,0,4,128,128,256);ctx[12:16]=bytes([wear,simple,red,1]);struct.pack_into('<IHHII',ctx,16,0xe400,64,48,0xe400+last*128,0x20000ed4)
 x=run(False,rows(pattern),bytes(ctx),address,size,mask);y=run(True,rows(pattern),bytes(ctx),address,size,mask);assert x==y,(pattern,simple,wear,red,last,pair,x,y);results.append(dict(inputs=[pattern,simple,wear,red,last,address,size,mask],result=x))
for c in json.loads((prior/'command7-results.json').read_text())['comparisons']:
 pattern,initialized,simple,mode,param,mask=c['inputs']
 if initialized!=1 or param!=0x1234 or mask!=0:continue
 storage=bytes.fromhex(c['result']['storage']);ctx=bytes.fromhex(c['result']['eeprom_context']);x=run(False,storage,ctx,0,8,0);y=run(True,storage,ctx,0,8,0);assert x==y,(c['inputs'],x,y);results.append(dict(after_command7=c['inputs'],ack=c['result']['ack'],deferred_status=c['result']['application_storage_status'],result=x))
r=dict(status='PASS_NATIVE_STOCK_READ_NO_FUNCTION_CUTS',cases=len(results),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),original_read_body_bytes_visited=len(visited),original_read_body_bytes=620,original_unvisited_ranges=[hex(x) for x in range(0x82e0,0x854c) if x not in visited],comparisons=results,limits=['Coherent128-byte physical/step geometry; logical rows4; wear1/2; bounded48-byte headers; valid context/provider.','Actual stock checksum/history/copy executes; no function entry cuts; no SROM request on read.','Fifty postcommand fixtures use synthetic write responses; no hardware durability or timing claim.','Returns, destination guards, context, SP, PRIMASK and unchanged storage compared; not byte-identical compilation.'])
(D/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(results),'read comparisons;',len(visited),'/620 original read bytes visited')

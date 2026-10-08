"""Original/independent/selected public RX bodies; completion-child boundary explicit."""
from pathlib import Path
import sys,struct,json,hashlib,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];fw=root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';blob=fw.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=Path(sys.argv[1]);segments=[];symbols={}
with elf.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
H=0x20002000;HW=0x40013800;BUF=0x20004004
entries={w:[0x08008998 if w==1 else 0x08008758,symbols['case_uart_rx'+str(w*8)],symbols['case_public_rx'+str(w*8)+'_v145']] for w in [1,2]}
def guest(state,count,mask,data,reception,idle,primask,rto):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x100000,0x10000);u.mem_map(0x40013000,0x1000)
 for a,b in segments:u.mem_write(a,b)
 u.mem_write(H,b'\xa5'*148);u.mem_write(H,struct.pack('<I',HW));u.mem_write(H+0x58,struct.pack('<IHHH',BUF,17,count,mask));u.mem_write(H+0x6c,struct.pack('<III',reception,0x55,0x08008999));u.mem_write(H+0x8c,struct.pack('<II',state,0xdeadbeef));u.mem_write(HW,struct.pack('<III',0x4000130,0x800000 if rto else 0,0x10000001));u.mem_write(HW+0x18,struct.pack('<IIII',0x11110000,0x10 if idle else 0,0xfeedface,data));u.mem_write(0x20004000,b'\xa7'*16);u.reg_write(UC_ARM_REG_PRIMASK,primask);return u
def run(u,a,original=False,require_atomic=True):
 writes=[];stopped=False
 def write(u,access,a,n,v,data):
  if HW<=a<HW+0x28:writes.append((hex(a),n,hex(v),u.reg_read(UC_ARM_REG_PRIMASK)))
  if require_atomic and a in (HW,HW+8):assert u.reg_read(UC_ARM_REG_PRIMASK)==1,('unmasked_atomic_write',hex(a))
 def code(u,a,n,data):
  nonlocal stopped
  if original and a in (0x08006544,0x08005e6a):
   u.mem_write(0x20003000,struct.pack('<II',1 if a==0x08006544 else 2,0 if a==0x08006544 else u.reg_read(UC_ARM_REG_R1)));stopped=True;u.emu_stop()
 u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_R0,H);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(a|1,0x20000000,count=10000);assert stopped or u.reg_read(UC_ARM_REG_PC)==0x20000000
 return (writes,bytes(u.mem_read(H,148)),bytes(u.mem_read(HW,0x28)),bytes(u.mem_read(0x20004000,16)),bytes(u.mem_read(0x20003000,8)),u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for width,state,count,mask,data,reception,idle,primask,rto in itertools.product([1,2],[0x20,0x22],[0,1,2,0xffff],[0,0x7f,0xff,0x1ff,0xffff],[0,0x1234,0xffff,0xffffffff],[0,1],[0,1],[0,1],[0,1]):
 vals=[run(guest(state,count,mask,data,reception,idle,primask,rto),a,m==0) for m,a in enumerate(entries[width])];assert vals[0]==vals[1]==vals[2],('rx',width,state,count,mask,data,reception,idle,primask,rto,[i for i,parts in enumerate(zip(*vals)) if len(set(str(x) for x in parts))>1]);rows.append(dict(kind='rx_three_way',width=width,initial_state=state,count=count,mask=hex(mask),data=hex(data),reception=reception,idle=idle,primask=primask,rto_enabled=rto,final_count=struct.unpack_from('<H',vals[0][1],0x5e)[0],final_pointer=hex(struct.unpack_from('<I',vals[0][1],0x58)[0]),callback_boundary=list(struct.unpack('<II',vals[0][4]))))
negative=[]
for width,version in itertools.product([1,2],['v140','v143','v144','v146','v147']):
 u=guest(0x22,1,0xff,0x5a,1,1,0,1);stock=run(u,entries[width][0],True);u=guest(0x22,1,0xff,0x5a,1,1,0,1);candidate=run(u,symbols['case_public_rx'+str(width*8)+'_'+version],require_atomic=False);assert stock!=candidate;negative.append(dict(width=width,version=version,different_fields=[i for i,(a,b) in enumerate(zip(stock,candidate)) if a!=b],stock_writes=stock[0],candidate_writes=candidate[0]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,rejected_candidate_controls=negative,firmware_sha256=hashlib.sha256(blob).hexdigest(),raw_sha256=hashlib.sha256(raw).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Complete RX helper bodies compared up to completion callback call; actual product callbacks08006544/08005e6a stop before their first instruction.','Native/public callbacks are compiled boundary markers, not recovered application callbacks. Original hook explicitly supplies matching marker metadata and stops, rather than pretending the callback returned.','Synthetic SRAM/USART registers; RDR/FIFO clearing, physical ISR scheduling and buffer allocation not modeled.','PRIMASK compared at atomic MMIO writes as well as after return; valid allocated caller buffers/alignment provided.','v1.4.5 agrees for this scoped behavior, not unique producer/compiler or full-SDK pin evidence.']),indent=2)+'\n');print('PASS',len(rows),'rejected revision controls',len(negative))

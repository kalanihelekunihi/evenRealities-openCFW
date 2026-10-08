from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-file-close/close.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
HEAP=0x20010000;SIZE=0x10000;QF=0x20006000;QH=0x20006100;T=0x20005000;LFS=0x20007000;CFG=0x20007100;OTHER=0x20007200;RET=0x2007f000
# The stock literal is source evidence for pxCurrentTCB; do not guess its address.
CURRENT=struct.unpack_from('<I',raw,0x45605c-0x438000)[0]
def run(native,recursive,flags,position,context,heap_mutex):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def call(a,args):
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1);u.emu_start(a|1,RET,count=300000);assert u.reg_read(UC_ARM_REG_PC)==RET,('setup did not return',hex(a),hex(u.reg_read(UC_ARM_REG_PC)));return u.reg_read(UC_ARM_REG_R0)
 def invalid(u,access,a,size,v,d):print('unmapped',hex(u.reg_read(UC_ARM_REG_PC)),hex(a));return False
 u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 w(0x20074a3c,1);w(0x20074a30,0);w(CURRENT,T)
 assert call(0x4d06ec,[HEAP,SIZE])==HEAP
 stream=call(0x4d0722,[HEAP,100]);assert HEAP<stream<HEAP+SIZE
 # Actual static mutex construction, not fabricated queue internals.
 assert call(0x4416f0,[4 if recursive else 1,QF])==QF
 assert call(0x4416f0,[4 if recursive else 1,QH])==QH
 w(0x200748f4,0 if context=='null_mutex' else QF|recursive);w(0x200748f8,0 if heap_mutex=='null' else QH|recursive);w(0x20074abc,HEAP)
 w(stream,LFS);f=stream+4;w(f,0);w(f+0x30,flags);w(f+0x50,CFG);w(CFG,0x20007300) # caller-owned file cache buffer, so backend skips cache free
 if position=='head':w(LFS+0x28,f)
 else:w(LFS+0x28,OTHER);w(OTHER,f)
 before=bytes(u.mem_read(HEAP,SIZE));calls=[];cuts=[]
 def hook(u,a,n,d):
  if a in [0x4497b6,0x44981c,0x4cfad0,0x4cdf74,0x474d16,0x4d0808]:calls.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if a not in [0x44981c,0x474d16] else None))
  if a==0x4733ee:cuts.append(('heap_mutex_error_log_entry',hex(a)));u.emu_stop()
  assert a not in [0x4420bc,0x5fa0a4,0x4d09b4],'unexpected yield/assert'
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_IPSR,15 if context=='isr' else 0);rv=call(sym['audio_file_close_selected'] if native else 0x4745f4,[stream]) if heap_mutex!='null' or context!='thread' else None
 if heap_mutex=='null' and context=='thread':
  u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1);u.emu_start((sym['audio_file_close_selected'] if native else 0x4745f4)|1,RET,count=300000);assert cuts==[('heap_mutex_error_log_entry','0x4733ee')]
 freed=any(a=='0x4d0808' for a,_,_ in calls)
 if context=='thread':assert word(LFS+0x28)==(0 if position=='head' else OTHER);assert word(OTHER)==0;assert freed==(heap_mutex!='null')
 else:assert rv==0xffffffff and not freed and bytes(u.mem_read(HEAP,SIZE))==before
 if freed:assert rv==0 and call(0x4d0722,[HEAP,100])==stream # actual reallocation of freed wrapper
 return dict(return_value=rv,calls=calls,boundary=cuts,freed=freed,stream=hex(stream),heap_sha256=hashlib.sha256(u.mem_read(HEAP,SIZE)).hexdigest(),lfs_list=hex(word(LFS+0x28)),other_next=hex(word(OTHER)),mutex_bytes=bytes(u.mem_read(QF,80)).hex()+bytes(u.mem_read(QH,80)).hex(),tcb_bytes=bytes(u.mem_read(T,112)).hex())
rows=[]
for recursive,flags,position,context,heap_mutex in itertools.product([0,1],[0,0x80000],['head','second'],['thread','null_mutex','isr'],['valid','null']):
 o=run(False,recursive,flags,position,context,heap_mutex);n=run(True,recursive,flags,position,context,heap_mutex);assert o==n,(recursive,flags,position,context,heap_mutex,o,n);rows.append(dict(recursive=recursive,file_flags=hex(flags),position=position,context=context,heap_mutex=heap_mutex,**o))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Actual static mutex create/take/release and TLSF create/malloc/free/reallocate, common original filesystem peers.','Constructed clean/error-marked file with caller-owned cache; no media I/O, dirty flush, pending waiters, live scheduling or callback concurrency.','Heap mutex rejection stops before error logger first instruction; no successful free or fabricated return.','Backend error return/free ordering is static source evidence, not injected backend failure.']),indent=2)+'\n');print('PASS',len(rows),'file close comparisons')

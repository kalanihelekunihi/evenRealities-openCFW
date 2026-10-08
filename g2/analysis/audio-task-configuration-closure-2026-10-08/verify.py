from pathlib import Path
import hashlib,json,struct
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];base=0x438000
# Decode authentic data identically to sealed Python reference; validates dictionary backreferences.
p=0x79189e;end=0x79430e;data=bytearray()
while p!=end:
 t=raw[p-base];p+=1;l=t&3;m=t>>4
 if not l:l=raw[p-base]+3;p+=1
 if m==15:m=raw[p-base]+15;p+=1
 for i in range(l-1):data.append(raw[p-base]);p+=1
 if m:
  o=raw[p-base];p+=1;hi=(t>>2)&3
  if hi==3:hi=raw[p-base];p+=1
  o+=hi<<8
  for i in range(m+2):data.append(data[-o])
assert hashlib.sha256(data).hexdigest()==json.loads((D.parent/'audio-dispatch-initializer-closure-2026-10-08/results.json').read_text())['decoded_sha256']
elf=Path('/tmp/opencfw-audio-config/config.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
rows=[]
for kind in ['thread','queue','terminate_other']:
 vals=[]
 for entry in [{'thread':0x53c344,'queue':0x53c3ee,'terminate_other':0x53c4f2}[kind],sym[{'thread':'audio_thread_init_selected','queue':'audio_resource_queue_prefix','terminate_other':'audio_thread_terminate_selected'}[kind]]]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(base,(len(raw)+4095)&~4095);u.mem_write(base,raw);u.mem_map(0x20000000,0x80000);u.mem_write(0x20000000,bytes(data));u.mem_map(0x2013b000,0x242000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000);u.mem_write(0x20004543,b'\x00');calls=[];boundary=[]
  for a,b in segments:u.mem_write(a,b)
  def code(u,a,n,d):
   if a==0x454820:
    sp=u.reg_read(UC_ARM_REG_SP);args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]+list(struct.unpack('<III',u.mem_read(sp,12)));calls.append([hex(a),args]);assert args==[0x53c52d,0x78ebb4,2048,0,47,0x20360e18,0x20072300]
   if a==0x456110:boundary.extend([hex(a),u.reg_read(UC_ARM_REG_R0)]);assert boundary==['0x456110',680];u.emu_stop()
   assert a not in [0x4420bc,0x43d574,0x43ce9e],'unexpected yield/logger'
  if kind=='terminate_other':
   # Build both tasks using real static creation, scheduler not started. Second higher priority task is current.
   def invoke(at,r0=0,r1=0,r2=0):
    u.reg_write(UC_ARM_REG_R0,r0);u.reg_write(UC_ARM_REG_R1,r1);u.reg_write(UC_ARM_REG_R2,r2);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(at|1,0x2007f000,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
   invoke(0x53c344)
   attrs=struct.pack('<9I',0x78ebb4,0,0x20073000,0x70,0x20364000,0x2000,48,0,0);u.mem_write(0x20005000,attrs);invoke(0x4490e2,0x53c52d,0,0x20005000)
   assert struct.unpack('<I',u.mem_read(0x20074a20,4))[0]==0x20073000
   def forbid_free(u,a,n,d):assert a!=0x456210,'unexpected free of static task'
   u.hook_add(UC_HOOK_CODE,forbid_free)
  u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(entry|1,0x2007f000,count=100000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
  def w(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  if kind=='terminate_other':assert w(0x20003fa0)==0;assert w(0x20074a30)==1;assert w(0x20074a20)==0x20073000;assert w(0x2006a49c+47*20)==0;assert w(0x2006a49c+48*20)==1;assert w(0x20072314)==0
  if kind=='thread':assert w(0x20003fa0)==0x20072300;assert w(0x20074a30)==1;assert w(0x20074a20)==0x20072300;assert w(0x2007232c)==47;assert w(0x20074a38)==47;assert w(0x2006a49c+47*20)==1;assert w(0x20072314)==0x2006a49c+47*20;assert w(0x20074a3c)==0;assert w(0x20072368)==0;assert bytes(u.mem_read(0x2007236c,1))==b'\x00'
  vals.append((calls,boundary,bytes(u.mem_read(0x20000000,0x75050)),bytes(u.mem_read(0x20360e18,8192))))
 assert vals[0]==vals[1],kind;rows.append(dict(kind=kind,calls=vals[0][0],boundary=vals[0][1],control_block='0x20072300' if kind=='thread' else None))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Authentic decompressed RAM data and zeroed BSS fixtures, one/two created static tasks in isolation, scheduler not started; noncurrent audio deletion tested. Not full boot, context switch or producer shutdown.','Actual shared static task creation kernel peers run; independent source covers first-party wrapper only.','Queue stops before allocator456110 with request680; no fabricated queue allocation return or timer initialization.']),indent=2)+'\n');print('PASS',len(rows))

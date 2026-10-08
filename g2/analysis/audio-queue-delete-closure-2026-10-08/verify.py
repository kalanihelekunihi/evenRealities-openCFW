from pathlib import Path
import itertools,struct,json,hashlib,sys
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path(sys.argv[1]);segments=[]
with elf.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[];B=0x20006000;Q=B+8;END=B+256;START=0x20074158
for static,merge,ipsr,null,nmsgs in itertools.product([0,1],range(4),[0,15],[0,1],[0,3]):
 vals=[]
 for entry in [0x449bec,sym['audio_queue_delete']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  # Allocated 128-byte heap block; optional adjacent free blocks, sorted end sentinel.
  w(B,0,0x80000080);w(Q+56,nmsgs);u.mem_write(Q+0x46,bytes([static]));w(END,0,0)
  left=B-64;right=B+128;w(START,left if merge&1 else right if merge&2 else END,0)
  if merge&1:w(left,right if merge&2 else END,64)
  if merge&2:w(right,END,128)
  w(0x2007465c,END);w(0x20074660,(64 if merge&1 else 0)+(128 if merge&2 else 0));w(0x2007466c,7)
  # scheduler task count zero: valid free/list operations but no pending task processing
  w(0x20074a30,0);w(0x20074a3c,1);w(0x20074a58,0);calls=[]
  def code(u,a,n,d):
   if a in [0x456210,0x4562da,0x454d7c,0x454dcc]:calls.append(hex(a))
   assert a not in [0x4420bc,0x45504c],'unexpected task/yield processing'
  u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_R0,0 if null else Q);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
  ret=u.reg_read(UC_ARM_REG_R0);free=struct.unpack('<I',u.mem_read(0x20074660,4))[0];count=struct.unpack('<I',u.mem_read(0x2007466c,4))[0]
  freed=not ipsr and not null and not static;assert ret==(0xfffffffa if ipsr else 0xfffffffc if null else 0);assert free==((64 if merge&1 else 0)+(128 if merge&2 else 0)+(128 if freed else 0));assert count==7+freed
  vals.append((ret,bytes(u.mem_read(B-64,328)),bytes(u.mem_read(START,8)),bytes(u.mem_read(0x2007465c,20)),bytes(u.mem_read(0x20074a58,4)),u.reg_read(UC_ARM_REG_BASEPRI)))
 assert vals[0]==vals[1],(static,merge,ipsr,null,nmsgs)
 rows.append(dict(static=static,adjacent_free_mask=merge,ipsr=ipsr,null=null,messages=nmsgs,freed=freed))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),valid_dynamic_frees=sum(r['freed'] for r in rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Coherent constructed heap; task count zero skips pending-ready/tick resume handling. No real audio lifecycle/producer quiescence.','No stubs; actual context, suspend/resume, original free and insertion run. Independent C reuses actual suspend/resume.','Queue fixtures specify allocation marker/count and allocated heap only, not whole initialized queue or active waiters. Static deletion no-op at selected kernel body.']),indent=2)+'\n');print('PASS',len(rows))

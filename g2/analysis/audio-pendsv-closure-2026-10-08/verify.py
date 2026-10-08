from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];assert struct.unpack_from('<I',raw,0x38)[0]==0x5fa0c9;elf=Path('/tmp/opencfw-audio-pendsv/context.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
A=0x20006000;B=0x20006100;READY=0x2006a49c;STACKA=0x20008000;PSPA=0x20009100;FRAMEB=0x2000a100;INPUT=0x20006200;OUT=0x20006300;RET=0x2007f000
regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];old=[0xa0000000+i for i in range(8)];new=[0xb0000000+i for i in range(8)]
fpregs=[getattr(__import__("unicorn.arm_const",fromlist=["x"]),"UC_ARM_REG_S"+str(i)) for i in range(16,32)]
oldfp=[0x3f800000+i for i in range(16)];newfp=[0x3f000000+i for i in range(16)]
def run(native,suspended,index,limit,offset,fp):
 excret=0xffffffed if fp else 0xfffffffd;savewords=26 if fp else 10
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
 def append(L,I,owner):w(I,0,L+8,L+8,owner,L);w(L,1,L+8,0xffffffff,I,I)
 for p in range(3):init(READY+20*p)
 append(READY+20,A+4,A);append(READY+40,B+4,B);w(A+0x2c,1);w(B+0x2c,2);w(A+0x30,STACKA);w(B+0x30,0x2000a000);w(STACKA,*([0xa5a5a5a5]*4));w(0x2000a000,*([0xa5a5a5a5]*4));w(A+0x58,0x11111111);w(B+0x58,0x22222222)
 psp=PSPA+offset;w(A,psp);w(B,FRAMEB);w(FRAMEB,0x2000a000,excret,*new,*(newfp if fp else []));w(INPUT,*old,*(oldfp if fp else []));w(0xe000ed88,0xf00000);w(0x20074a20,A);w(0x20074a38,2);w(0x20074a58,suspended);w(0x20074a5c,index);w(0x20074a44,1)
 # Real M33 architectural seed instruction, no skipped/modified firmware instructions.
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1);u.reg_write(UC_ARM_REG_R0,limit);u.emu_start(sym['audio_fixture_seed_psplim']|1,RET,count=1000);assert u.reg_read(UC_ARM_REG_PC)==RET
 u.reg_write(UC_ARM_REG_LR,RET|1);u.emu_start(sym['audio_fixture_read_psplim']|1,RET,count=1000);assert u.reg_read(UC_ARM_REG_R0)==limit
 boundary=[]
 def hook(u,a,n,d):
  if a==0x5fa11e:boundary.append('before_exception_return');u.emu_stop()
  assert a not in [0x46d86c,0x5fa0a4],'unexpected stack canary/ready assertion'
 u.hook_add(UC_HOOK_CODE,hook)
 if native:
  w(0x2007e000,OUT);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[psp,limit,excret,INPUT]):u.reg_write(r,v)
  u.emu_start(sym['audio_pendsv_integer_model']|1,RET,count=30000);assert u.reg_read(UC_ARM_REG_PC)==RET;restored=list(struct.unpack('<'+('27I' if fp else '11I'),u.mem_read(OUT,108 if fp else 44)))
 else:
  u.reg_write(UC_ARM_REG_PSP,psp);u.reg_write(UC_ARM_REG_LR,excret);u.reg_write(UC_ARM_REG_IPSR,14)
  for r,v in zip(regs,old):u.reg_write(r,v)
  if fp:
   for r,v in zip(fpregs,oldfp):u.reg_write(r,v)
  u.emu_start(0x5fa0c9,RET,count=30000);assert boundary==['before_exception_return']
  restored=[u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3),*[u.reg_read(r) for r in regs],u.reg_read(UC_ARM_REG_PSP)]+([u.reg_read(r) for r in fpregs] if fp else [])
  assert u.reg_read(UC_ARM_REG_BASEPRI)==0
  u.reg_write(UC_ARM_REG_IPSR,0);u.reg_write(UC_ARM_REG_LR,RET|1);u.emu_start(sym['audio_fixture_read_psplim']|1,RET,count=1000);assert u.reg_read(UC_ARM_REG_R0)==restored[0]
 expected=[limit,excret,*old,psp,*(oldfp if fp else [])] if suspended else [0x2000a000,excret,*new,FRAMEB+savewords*4,*(newfp if fp else [])];assert restored==expected
 assert word(0x20074a20)==(A if suspended else B);assert word(A)==psp-savewords*4
 assert list(struct.unpack('<'+str(savewords)+'I',u.mem_read(psp-savewords*4,savewords*4)))==[limit,excret,*old,*(oldfp if fp else [])]
 return (restored,bytes(u.mem_read(A,256+112)),bytes(u.mem_read(READY,60)),bytes(u.mem_read(0x20074a20,64)),bytes(u.mem_read(0x2006f348,512)),bytes(u.mem_read(psp-savewords*4,savewords*4)))
rows=[]
for suspended,index,limit,offset,fp in itertools.product([0,1],[0,63],[0,STACKA],[0,8],[0,1]):
 o=run(False,suspended,index,limit,offset,fp);n=run(True,suspended,index,limit,offset,fp);assert o==n,(suspended,index,limit,offset);rows.append(dict(suspended=suspended,history_index=index,psplim=hex(limit),psp_offset=offset,fp_context=fp,restored=[hex(v) for v in o[0]],original_boundary='before_exception_return'))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,cpu_profile='Cortex-M33 ARMv8-M compatible selected context instructions; firmware Apollo M55',elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Actual PendSV save, actual scheduler selector, actual register/PSPLIM/PSP restore through boundary before BX EXC_RETURN; no instruction skip or child result stub.','Independent C functional context model and ready selector; not a deployable interrupt handler.','Synthetic coherent two-task ready lists, valid canaries and history ring; no hardware exception entry/return, FP arithmetic/lazy hardware stacking, live scheduling, timeout or external producers.']),indent=2)+'\n');print('PASS',len(rows),'PendSV context prefix comparisons')

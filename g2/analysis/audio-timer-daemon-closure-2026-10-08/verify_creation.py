from pathlib import Path
import json,hashlib,struct
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-timer-daemon/daemon.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
vals=[]
for entry in [0x47e674,sym['audio_daemon_create_selected']]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000);u.mem_write(0x20074ab0,struct.pack('<I',0x20006000));calls=[]
 for a,b in segments:u.mem_write(a,b)
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def hook(u,a,n,d):
  if a==0x454820:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]+list(struct.unpack('<III',u.mem_read(u.reg_read(UC_ARM_REG_SP),12)));calls.append([hex(v) for v in args]);assert args==[0x47e879,0x78ebcc,4096,0,54,0x2003fa98,0x20071ea0]
  assert a not in [0x4420bc,0x456110],'unexpected yield/dynamic allocation'
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(entry|1,0x2007f000,count=200000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==1
 assert word(0x20074ab4)==0x20071ea0 and word(0x20074a20)==0x20071ea0 and word(0x20071ecc)==54 and word(0x2006a49c+20*54)==1 and word(0x20074a30)==1 and word(0x20074a3c)==0
 vals.append((calls,bytes(u.mem_read(0x20000000,0x75050))))
assert vals[0]==vals[1]
(D/'creation-results.json').write_text(json.dumps(dict(status='PASS',cases=1,calls=vals[0][0],current_tcb='0x20071ea0',priority=54,stack_base='0x2003fa98',stack_bytes=16384,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Actual original constructor/static memory/static create and independent selected constructor; initialized-queue/isolated zero-BSS fixture, scheduler not started.','No fake task creation success, dynamic allocation, task context execution, real population or live scheduling.','Whole selected RAM region matches except excluded main-stack scratch; shared actual creation peers, not independent entire kernel create.']),indent=2)+'\n');print('PASS 1 actual timer task creation comparison')

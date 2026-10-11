#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2];A=R/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-events-a'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
src=R/'g2/components/bootloader/initializer_callbacks/startup_runtime.c';event=R/'g2/components/bootloader/initializer_callbacks/pcm22_fp_native/startup_events_a.c'
out=H/'event-selected';out.mkdir(exist_ok=True);cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
sources=[src,event,A/'startup_event_a_trim.c',A/'startup_event_a_transitions.c',A/'startup_event_a_sequence8.c',R/'g2/components/bootloader/platform_control/critical_save.S']
objs=[];commands=[]
for n,p in enumerate(sources):
 obj=out/f'entry_{n}.o';cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfpu=fpv5-sp-d16','-mfloat-abi=hard','-ffreestanding','-fno-builtin','-fdata-sections','-ffunction-sections','-O0','-c',str(p),'-o',str(obj)]
 subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);commands.append(cmd);objs.append(obj)
elf=out/'event_dispatch_selected.elf';link=['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_startup_spot_dispatch','--gc-sections','--undefined=event_a_state_transition_sequence','--undefined=event_a_temperature_transition_separate','--undefined=event_a_transition_sequence_24','--undefined=event_a_transition_sequence_8_timer_disabled','--unresolved-symbols=ignore-all','--defsym=spotmgr_init_42abbc_native=0x30001','-o',str(elf),*[str(x) for x in objs]]
subprocess.run(link,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);commands.append(link)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,rev,var,mode,magic,first_ret):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000,0x10000);u.mem_map(0x30000,0x10000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.mem_map(0x40000000,0x100000)
 def w(p,x):u.mem_write(p,struct.pack('<I',x))
 def rd(p):return struct.unpack('<I',u.mem_read(p,4))[0]
 w(0x4002000c,rev);w(0x20000098,var);w(0x40021108,mode);w(0x20026ba0,magic)
 u.mem_write(0x20026e38,b'\xa5'*60);u.reg_write(UC_ARM_REG_SP,0x2003eff0);u.reg_write(UC_ARM_REG_LR,0x8000001);u.reg_write(UC_ARM_REG_PRIMASK,0);u.reg_write(UC_ARM_REG_FPSCR,0)
 def hook(emu,pc,size,data):
  if pc in (0x42abbc,0x30000):emu.reg_write(UC_ARM_REG_R0,first_ret);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((sym['opencfw_boot_startup_spot_dispatch'] if source else 0x41ce52)|1,0x8000000,count=30000)
 target=rd(0x20026e3c);assert target==((sym['opencfw_boot_spotmgr_power_state_update_a']|1) if source else 0x42a879)
 state=[u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200271a9,6)).hex(),rd(0x40020028),rd(0x40020060)]
 before=bytes(u.mem_read(0x20026e38,60));u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_LR,0x8000001)
 u.emu_start(target,0x8000000,count=3000)
 assert bytes(u.mem_read(0x20026e38,60))==before
 state.extend((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_FPSCR)))
 return state
cases=[]
for rev,var in ((35,2),(36,0)):
 for mode,magic,first_ret in itertools.product((0,0x30),(0,0x1f01600d),(0,7)):
  a,b=run(False,rev,var,mode,magic,first_ret),run(True,rev,var,mode,magic,first_ret)
  assert a==b,(rev,var,mode,magic,first_ret,a,b)
  cases.append((rev,var,mode,magic,first_ret))
receipt=dict(status='PASS',cases=len(cases),stock_image_sha256=hashlib.sha256(blob).hexdigest(),selected_event_sha256=hashlib.sha256(event.read_bytes()).hexdigest(),startup_source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),commands=commands,limits='Installed-pointer plus guarded public callback effect for PCM2.2 routes. Full callback branch matrix is separately compared by retained verify_event_a_native.py on this exact combined ELF; its selected current source file is used here. Root power initialize, other slots and physical silicon remain open.')
(out/'event-slot-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS startup event slot',len(cases))

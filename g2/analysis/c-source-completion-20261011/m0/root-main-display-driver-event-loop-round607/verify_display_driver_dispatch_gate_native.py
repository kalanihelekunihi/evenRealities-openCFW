#!/usr/bin/env python3
"""Compare linked Apollo uLED gate, wear and case-state C against native."""
from pathlib import Path
import itertools,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).with_name('display_driver_dispatch_gate.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
providers=[('audio_uart_command_pending',0x4abe60,'command'),
 ('audio_ota_transfer_active',0x4487ac,'ota'),
 ('audio_log_flags',0x43d0ce,'flags'),
 ('audio_log_extended',0x43d574,'text'),
 ('compressed_log_output',0x43ce9e,'compact')]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n,_,_ in providers))
 image=d/'gate.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),
  *[str(source.with_name(n)) for n in ('display_driver_wear_detect.c',
      'display_driver_case_status.c','display_driver_settings_live.c')],
  str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for command,ota,wear,case in itertools.product((0,1),repeat=4):
  for flags in (0,1,2,4,7):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    settings=syms['audio_settings_config_live'] if compiled else 0x20072da8
    wear_mode=syms['display_driver_wear_mode_cell'] if compiled else 0x20074edc
    case_state=syms['display_driver_case_state_cells'] if compiled else 0x20074188
    case_override=syms['display_driver_case_override_cell'] if compiled else 0x20075012
    cpu.mem_write(settings+0x14,bytes([0 if wear else 1]))
    cpu.mem_write(wear_mode,(0).to_bytes(4,'little'))
    cpu.mem_write(case_state+6,bytes([0,1 if case else 0]))
    cpu.mem_write(case_override,bytes([0]))
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    target={((syms[n] if compiled else addr)&~1):kind for n,addr,kind in providers}
    events=[]
    def cs(u,p):return bytes(u.mem_read(p,180)).split(b'\0')[0].decode('ascii')
    def hook(u,address,_size,_user):
     kind=target.get(address)
     if kind is None:return
     if kind in ('command','ota','flags'):
      events.append((kind,))
      u.reg_write(UC_ARM_REG_R0,{'command':command,'ota':ota,'wear':wear,
                                 'case':case,'flags':flags}[kind])
     elif kind=='text':
      sp=u.reg_read(UC_ARM_REG_SP)
      assert cs(u,u.reg_read(UC_ARM_REG_R1))=='service.settings'
      assert cs(u,u.reg_read(UC_ARM_REG_R3))=='SVC_Settings_UledCtrlCheck'
      events.append(('text',u.reg_read(UC_ARM_REG_R0),
        int.from_bytes(u.mem_read(sp,4),'little'),
        cs(u,int.from_bytes(u.mem_read(sp+4,4),'little'))))
     elif kind=='compact':
      assert u.reg_read(UC_ARM_REG_R1)==u.reg_read(UC_ARM_REG_R2)
      events.append(('compact',u.reg_read(UC_ARM_REG_R0),cs(u,u.reg_read(UC_ARM_REG_R1))))
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    start=syms['display_driver_dispatch_gate'] if compiled else 0x46b238
    cpu.emu_start(start|1,0x600000,count=300)
    observations.append((events,cpu.reg_read(UC_ARM_REG_R0)))
   assert observations[0]==observations[1],((command,ota,wear,case,flags),observations)
   count+=1
print('PASS_DISPLAY_DRIVER_DISPATCH_GATE_NATIVE',count)

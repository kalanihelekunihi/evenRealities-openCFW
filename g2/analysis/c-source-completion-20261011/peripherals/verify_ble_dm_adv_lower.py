"""Actual ARM compiled-C/native Cordio DM advertising init comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_dm_adv_lower.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('#include <stdint.h>\nuint8_t audio_ble_dm_adv_control[64],audio_ble_dm_handler_state[64];\n')
 elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_dm_adv_lower',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for kind in ('whole','cb0','cb1'):
  for initial in (0,0x75):
   rows=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    ctl=syms['audio_ble_dm_adv_control'] if compiled else 0x20073394
    state=syms['audio_ble_dm_handler_state'] if compiled else 0x20073b78
    u.mem_write(ctl,b'X'*64);u.mem_write(state,b'Y'*64);u.mem_write(state+12,bytes([initial]))
    u.reg_write(UC_ARM_REG_R0,1 if kind=='cb1' else 0)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    start=(syms['audio_ble_dm_adv_lower'] if compiled else 0x4b30e4) if kind=='whole' else (syms['audio_ble_dm_adv_callback_init'] if compiled else 0x4b3098)
    u.emu_start(start|1,0x600000,count=1000)
    rows.append((bytes(u.mem_read(ctl,64)),bytes(u.mem_read(state,64))))
   assert rows[0]==rows[1],(kind,initial)
   print('PASS',kind,hex(initial))

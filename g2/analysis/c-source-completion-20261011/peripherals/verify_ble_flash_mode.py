"""Bounded compiled C/native flash-mode entry/exit, with HAL control cut."""
from pathlib import Path
import struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[3]
BLOB = (ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c'
    shim.write_text('''#include <stdint.h>
uint8_t audio_ble_flash_mode;
uint32_t audio_ble_flash_control(uint32_t a,uint32_t b,const uint32_t *p){(void)a;(void)b;(void)p;return 0;}
''')
    elf=Path(td)/'a.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_flash_enter_program_mode',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_flash_mode.c'),str(shim),'-o',str(elf)],check=True)
    syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for operation in ('enter','leave'):
        for mode,status in ((0,0),(1,0),(1,0x80)):
            observations=[]
            for compiled in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                u.mem_map(0x40021000,0x1000)
                for a,d in segs:u.mem_write(a,d)
                u.mem_write(0x20074f62,bytes([mode]))
                u.mem_write(syms['audio_ble_flash_mode'],bytes([mode]))
                u.mem_write(0x40021018,struct.pack('<I',status))
                u.mem_write(0x40021014,struct.pack('<I',0x33))
                cut=(syms['audio_ble_flash_control']&~1) if compiled else 0x480312
                calls=[]
                def hook(uc,a,size,_):
                    if a==cut:
                        r0,r1,r2=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
                        calls.append((r0,r1,struct.unpack('<I',uc.mem_read(r2,4))[0]))
                        uc.reg_write(UC_ARM_REG_R0,0)
                        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                start=(syms['audio_ble_flash_enter_program_mode'] if operation=='enter' else syms['audio_ble_flash_leave_program_mode']) if compiled else (0x47f3c6 if operation=='enter' else 0x47f418)
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.emu_start(start|1,0x600000,count=120000)
                observations.append((u.reg_read(UC_ARM_REG_R0),calls,struct.unpack('<I',u.mem_read(0x40021014,4))[0]))
            assert observations[0]==observations[1],(operation,mode,status,observations)
            print('PASS flash mode',operation,mode,hex(status))

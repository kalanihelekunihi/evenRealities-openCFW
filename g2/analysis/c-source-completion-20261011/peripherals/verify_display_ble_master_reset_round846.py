#!/usr/bin/env python3
"""Compare Apollo BLE master row reset 0x503540 with source C."""
from pathlib import Path
import hashlib,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_master_reset.c'
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);stub=temp/'stub.c'
    stub.write_text('#include <stdint.h>\nvolatile uint8_t audio_ble_subsystem_state_20071670[0xa0];\n')
    elf=temp/'fixture.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_ble_master_child_503540',str(src),str(stub),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        obj=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for seed in (0,0x55,0xa5,0xff):
        pair=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
            u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for address,data in segments:u.mem_write(address,data)
            state=symbols['audio_ble_subsystem_state_20071670'] if compiled else 0x20071670
            u.mem_write(state,bytes((seed+i)&255 for i in range(0xa0)))
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.emu_start((symbols['audio_ble_master_child_503540'] if compiled else 0x503540)|1,0x600000,count=3000)
            pair.append(bytes(u.mem_read(state,0xa0)))
        assert pair[0]==pair[1],(seed,pair)
        cases+=1
print('PASS_DISPLAY_BLE_MASTER_RESET_NATIVE',cases)

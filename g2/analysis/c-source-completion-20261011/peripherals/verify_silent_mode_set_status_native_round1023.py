#!/usr/bin/env python3
"""Compare compiled SilentMode_SetStatus byte effects with official Thumb."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/silent-mode-set-status-native-round1023';out.mkdir(parents=True,exist_ok=True)
srcdir=root/'components/audio/uart_thread_source_candidate'
sources=[srcdir/'silent_mode_set_status_4691bc.c',srcdir/'silent_mode_status_get_46919e.c']
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';storage=td/'storage.c';stubs=td/'stubs.s'
    storage.write_text('#include <stdint.h>\nuint8_t audio_settings_config_live[80];\n')
    names=['audio_log_flags','audio_log_extended','compressed_log_output']
    lines=['.syntax unified','.thumb','.section .text.oracle_stubs,"ax",%progbits']
    for name in names:lines += [f'.global {name}','.thumb_func',f'{name}:','  movs r0,#0','  bx lr']
    lines+=['.section .note.GNU-stack,"",%progbits'];stubs.write_text('\n'.join(lines)+'\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_silent_mode_set_status',
                    *map(str,sources),str(storage),str(stubs),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    cases=[0,1,2,255,0x100,0x101]
    for value in cases:
        outputs=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            cell=(sym['audio_settings_config_live'] if compiled else 0x20072da8)+0x15
            u.mem_write(cell,b'\x7a')
            u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_SP,0x200ff000)
            u.reg_write(UC_ARM_REG_LR,0x600001)
            entry=sym['audio_silent_mode_set_status'] if compiled else 0x4691bc
            u.emu_start(entry|1,0x600000,count=3000)
            outputs.append(bytes(u.mem_read(cell,1)))
        assert outputs[0]==outputs[1]==bytes([int((value&255)!=0)]),(value,outputs)
receipt={'round':1023,'status':'PASS_SILENT_MODE_SET_STATUS_NATIVE',
         'component':'Apollo silent-mode settings byte writer effects',
         'source':[str(s.relative_to(root)) for s in sources],
         'source_sha256':{s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in sources},
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x4691bc','values':cases,
         'validation':'Actual compiled Cortex-M4 C versus official Thumb config byte effects',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Null-config logging branch is unreachable with the fixed native config getter and not exercised',
                  'Full image placement and hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases))

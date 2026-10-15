#!/usr/bin/env python3
"""Compare compiled settings/status getters with official Apollo Thumb."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/silent-mode-status-get-native-round1019';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/silent_mode_status_get_46919e.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';storage=td/'storage.c'
    storage.write_text('#include <stdint.h>\nuint8_t audio_settings_config_live[80];\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_silent_mode_status_get',
                    str(src),str(storage),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    results=[]
    for value in (0,1,2,0x7f,0xff):
        values=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            config=sym['audio_settings_config_live'] if compiled else 0x20072da8
            u.mem_write(config+0x15,bytes([value]))
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            entry=sym['audio_silent_mode_status_get'] if compiled else 0x46919e
            u.emu_start(entry|1,0x600000,count=3000)
            values.append(u.reg_read(UC_ARM_REG_R0))
        assert values[0]==values[1]==(value!=0),(value,values)
        results.append({'config_byte':value,'status':values[0]})
receipt={'round':1019,'status':'PASS_SILENT_MODE_STATUS_GET_NATIVE',
         'component':'Apollo silent-mode status getter byte semantics',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x46919e','cases':results,
         'validation':'Actual compiled Cortex-M4 C versus official Thumb return for five config-byte states',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Full config allocation extent and image placement remain open',
                  'Full image/hardware proof remains open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(results))

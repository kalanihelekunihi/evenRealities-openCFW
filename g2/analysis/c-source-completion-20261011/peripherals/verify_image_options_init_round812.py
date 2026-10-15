#!/usr/bin/env python3
"""Compare native and C LVGL image descriptor initialization."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image_options_init.c'
out=Path(__file__).resolve().parent/'root-image-options-init-round812';out.mkdir(exist_ok=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
    elf_path=Path(tmp)/'image.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x110000',
                    str(source),'-o',str(elf_path)],check=True)
    with elf_path.open('rb') as fp:
        elf=ELFFile(fp)
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    def run(original,seed):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,data in segments:u.mem_write(a,data)
        u.mem_map(0x20000000,0x200000)
        p=0x20010000;u.mem_write(p,bytes([seed])*0x100)
        u.reg_write(UC_ARM_REG_CPSR,0x33)
        u.reg_write(UC_ARM_REG_R0,p)
        u.reg_write(UC_ARM_REG_SP,0x201ff000)
        u.reg_write(UC_ARM_REG_LR,0x600001)
        entry=0x488918 if original else symbols['audio_uart_ambiq_image_options_init_488918']
        u.emu_start(entry|1,0x600000,count=500)
        assert u.reg_read(UC_ARM_REG_PC)==0x600000
        return bytes(u.mem_read(p,0x100)),u.reg_read(UC_ARM_REG_SP)
    for seed in (0,1,0x5a,0xff):
        actual=run(True,seed);candidate=run(False,seed)
        if actual!=candidate:
            (out/'mismatch.json').write_text(json.dumps({'seed':seed,
                'native':actual[0].hex(),'candidate':candidate[0].hex(),
                'native_sp':actual[1],'candidate_sp':candidate[1]},indent=2)+'\n')
            raise AssertionError(seed)
receipt={'status':'PASS_NATIVE_IMAGE_OPTIONS_INIT','cases':4,
         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'native_blob_sha256':hashlib.sha256(blob).hexdigest(),
         'bounds':'Full 256-byte descriptor guard and SP; return register not compared.',
         'limits':['No image decoder or hardware proof.']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],4)

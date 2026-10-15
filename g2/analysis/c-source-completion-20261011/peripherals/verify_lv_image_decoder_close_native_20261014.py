#!/usr/bin/env python3
"""Compare image decoder close 0x48908c with its source-owned C body."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_close.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lower=[('audio_uart_lv_image_cache_enabled_4d4b24',0x4d4b24),
       ('audio_uart_lv_decoder_release_4d4e72',0x4d4e72)]
with tempfile.TemporaryDirectory() as directory:
    stub=Path(directory)/'lower.c'
    stub.write_text('typedef unsigned u32;\n'+'\n'.join(
        f'u32 {name}(u32 a,u32 b,u32 c){{return 0;}}' for name,_ in lower))
    image=Path(directory)/'close.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],
                   check=True,capture_output=True)
    with image.open('rb') as file:
        elf=ELFFile(file)
        segments=[(segment['p_vaddr'],segment.data()) for segment in elf.iter_segments()
                  if segment['p_type']=='PT_LOAD']
        symbols={sym.name:sym['st_value']
                 for sym in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled,has_decoder,callback,context,owner,resource):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        result,decoder,callback_address=0x20005000,0x20006000,0x20007000
        data=bytearray(80)
        def put(off,val):data[off:off+4]=val.to_bytes(4,'little')
        put(0,decoder if has_decoder else 0);put(0x40,owner);put(0x44,resource)
        uc.mem_write(result,bytes(data))
        uc.mem_write(decoder+12,(callback_address|1 if callback else 0).to_bytes(4,'little'))
        calls=[]
        def hook(emu,address,size,user):
            if address==callback_address:
                calls.append(('callback',emu.reg_read(UC_ARM_REG_R0)==decoder,
                              emu.reg_read(UC_ARM_REG_R1)==result))
                value=0
            else:
                name=next(name for name,native in lower
                          if (symbols[name]&~1 if compiled else native)==address)
                if name==lower[0][0]:
                    calls.append(('context',));value=context
                else:
                    calls.append(('release',emu.reg_read(UC_ARM_REG_R0),
                                  emu.reg_read(UC_ARM_REG_R1),emu.reg_read(UC_ARM_REG_R2)))
                    value=0
            emu.reg_write(UC_ARM_REG_R0,value)
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        for name,native in lower:
            target=symbols[name]&~1 if compiled else native
            uc.hook_add(UC_HOOK_CODE,hook,begin=target,end=target)
        uc.hook_add(UC_HOOK_CODE,hook,begin=callback_address,end=callback_address)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        uc.reg_write(UC_ARM_REG_R0,result)
        entry=symbols['audio_uart_lv_image_decoder_close_48908c'] if compiled else 0x48908c
        uc.emu_start(entry|1,0x600000,count=200)
        return calls

    cases=0
    for has_decoder in (False,True):
        for callback in (False,True):
            for context in (0,1):
                for owner in (0,0x20009000):
                    for resource in (0,0x2000a000):
                        args=(has_decoder,callback,context,owner,resource)
                        native=run(False,*args);candidate=run(True,*args)
                        assert native==candidate,(args,native,candidate)
                        cases+=1
    print('PASS_LV_IMAGE_DECODER_CLOSE_NATIVE',cases)

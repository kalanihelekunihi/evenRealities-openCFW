#!/usr/bin/env python3
"""Compare LVGL cache entry accessor 0x4d5396 with Apollo S200."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/cache_entry.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
    stub=Path(directory)/'log.c'
    stub.write_text('unsigned audio_uart_lvgl_log(unsigned a,unsigned b,unsigned c,unsigned d,unsigned e,unsigned f,unsigned g){return 0;}\n')
    image=Path(directory)/'entry.elf'
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

    def run(compiled,entry,offset):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
        uc.mem_map(0x100000,0x200000);uc.mem_map(0x20000000,0x100000)
        for address,data in segments:uc.mem_write(address,data)
        base=0x20005000;uc.mem_write(base+8,offset.to_bytes(4,'little'))
        calls=[]
        def cstr(emu,address):return bytes(emu.mem_read(address,150)).split(b'\0',1)[0]
        def log(emu,address,size,user):
            r=[emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,
                                               UC_ARM_REG_R2,UC_ARM_REG_R3)]
            sp=emu.reg_read(UC_ARM_REG_SP)
            extra=[int.from_bytes(emu.mem_read(sp+4*i,4),'little') for i in range(3)]
            calls.append((r[0],cstr(emu,r[1]),r[2],cstr(emu,r[3]),
                          tuple(cstr(emu,p) for p in extra)))
            emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
        target=symbols['audio_uart_lvgl_log']&~1 if compiled else 0x44d25c
        uc.hook_add(UC_HOOK_CODE,log,begin=target,end=target)
        uc.reg_write(UC_ARM_REG_SP,0x200ff000);uc.reg_write(UC_ARM_REG_LR,0x600001)
        uc.reg_write(UC_ARM_REG_R0,base if entry else 0)
        start=symbols['audio_uart_lv_cache_entry_4d5396'] if compiled else 0x4d5396
        try:uc.emu_start(start|1,0x600000,count=80);terminal='return'
        except UcError:terminal='fault'
        return calls,terminal,(uc.reg_read(UC_ARM_REG_R0) if terminal=='return' else None)

    cases=0
    for entry in (False,True):
        for offset in (0,4,0x40,0xffffffff):
            args=(entry,offset);native=run(False,*args);candidate=run(True,*args)
            assert native==candidate,(args,native,candidate)
            cases+=1
    print('PASS_LV_CACHE_ENTRY_NATIVE',cases)

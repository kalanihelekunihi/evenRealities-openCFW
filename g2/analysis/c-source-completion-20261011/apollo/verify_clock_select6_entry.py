#!/usr/bin/env python3
"""Bounded stock/source class-6 clock selection with supplied config."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_PRIMASK,
                               UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP)
ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/initializer_callbacks/startup_clock_config.c'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == LOCKED
with tempfile.TemporaryDirectory(prefix='boot-clock-select6-') as td:
    d = Path(td)
    obj, stubs, elfpath = d/'config.o', d/'stubs.o', d/'config.elf'
    cc = ['clang','--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb',
          '-mfpu=fpv5-sp-d16','-mfloat-abi=softfp']
    subprocess.run(cc+['-O2','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(obj)],check=True)
    names=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
    assembly=d/'stubs.S'
    assembly.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
        f'.global {name}\n.thumb_func\n{name}:\nbx lr\n' for name in names))
    subprocess.run(cc+['-c',str(assembly),'-o',str(stubs)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x500000',str(obj),str(stubs),'-o',str(elfpath)],check=True,stderr=subprocess.DEVNULL)
    with elfpath.open('rb') as stream:
        elf=ELFFile(stream)
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
    cases=[]
    for label,rate,config,ref0,ref1,user in [
        ('explicit-mode0',48000000,bytes([0,2,1,0,0x55,0x44,0x33,0x22,0,0,0,0]),24000000,0,0),
        ('explicit-mode1',96000000,bytes([1,4,0,0,0xaa,0xbb,0xcc,0xdd,0,0,0,0]),0,24000000,0),
        ('missing-mode0-ref',48000000,bytes(12),0,0,0),
        ('missing-mode1-ref',48000000,bytes([1])+bytes(11),0,0,0),
        ('existing-user',48000000,bytes(12),24000000,0,1),
        ('zero-rate',0,bytes(12),24000000,0,0),
    ]:
        pair=[]
        for native in (True,False):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
            u.mem_map(0x410000,0x40000);u.mem_write(0x410000,STOCK.read_bytes())
            u.mem_map(0x500000,0x10000)
            if not native:
                for address,data in segments:u.mem_write(address,data)
            u.mem_map(0x20000000,0x40000)
            u.mem_write(0x20000080,struct.pack('<I',ref0))
            u.mem_write(0x2000008c,struct.pack('<I',ref1))
            u.mem_write(0x20026ea4,struct.pack('<I',user))
            u.mem_write(0x20010000,config)
            u.reg_write(UC_ARM_REG_R0,rate)
            u.reg_write(UC_ARM_REG_R1,0x20010000)
            u.reg_write(UC_ARM_REG_PRIMASK,1)
            u.reg_write(UC_ARM_REG_SP,0x2002f000)
            u.reg_write(UC_ARM_REG_LR,0x50f001)
            entry=0x421978 if native else symbols['opencfw_boot_startup_select6']&~1
            u.emu_start(entry|1,0x50f000,count=10000)
            pair.append({'return':u.reg_read(UC_ARM_REG_R0),
                         'primask':u.reg_read(UC_ARM_REG_PRIMASK),
                         'config':bytes(u.mem_read(0x20027004,12)).hex(),
                         'rate':bytes(u.mem_read(0x20027038,4)).hex(),
                         'enabled':bytes(u.mem_read(0x2002719a,1)).hex()})
        assert pair[0]==pair[1],(label,pair)
        cases.append({'case':label,'result':pair[0]})
    report={'status':'PASS_BOUNDED_CLOCK_SELECT6','cases':cases,
            'original_sha256':LOCKED,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'source_elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),
            'limits':['Supplied 12-byte config paths only; automatic PLL generator and physical PLL lock are not exercised.','No live clock transition or hardware timing proof.']}
    Path(__file__).with_name('clock-select6-entry-oracle.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'cases':len(cases)}))

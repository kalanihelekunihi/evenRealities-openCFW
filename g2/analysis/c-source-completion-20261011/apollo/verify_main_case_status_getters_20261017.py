#!/usr/bin/env python3
"""Stock/C oracle for the three Case status-row byte getters."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_status_getters_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-status-getters/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
FUNCS=[('audio_uart_case_soc_4acaa0',0x4acaa0),
       ('audio_uart_case_charge_4acaac',0x4acaac),
       ('audio_uart_case_lid_4acab4',0x4acab4)]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'getters.elf'
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
         '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
         '-nostdlib','-Wl,-Ttext=0x100000',
         '-Wl,--defsym=audio_uart_case_soc_cell_2007418c=0x2007418c',
         '-Wl,--defsym=audio_uart_case_charge_cell_2007418d=0x2007418d',
         '-Wl,--defsym=audio_uart_case_sensor_b=0x2007418e']
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,name,addr,values):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x20000)
        for a,data in segs:u.mem_write(a,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(0x2007418c,bytes(values))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=addr if native else syms[name]&~1
        u.emu_start(entry|1,0x130000,count=100)
        return u.reg_read(UC_ARM_REG_R0)
    cases=0
    for a in (0,1,255):
        for b in (0,1,255):
            for c in (0,1,255):
                for name,addr in FUNCS:
                    values=(a,b,c)
                    stock=run(True,name,addr,values);rebuilt=run(False,name,addr,values)
                    if stock!=rebuilt:raise AssertionError((name,values,stock,rebuilt))
                    cases+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_STATUS_GETTERS_C','cases':cases,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'three one-byte getters over 27 status-row combinations',
         'remaining_gate':'SOC and charge RAM initialization and absolute placement at 0x2007418c/8d remain unverified.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],cases,sha(OUT))

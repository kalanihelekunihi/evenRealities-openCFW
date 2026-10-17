#!/usr/bin/env python3
"""Bounded stock/C call-order oracle for Case graphics refresh 0x4abf86."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_refresh_4abf86_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-refresh/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_log_wake_allowed','audio_uart_case_status','audio_wear_child_46b0ec',
       'audio_wear_child_47432c','audio_wear_child_474100']
STOCK_ADDR=[0x443484,0x4acad0,0x46b0ec,0x47432c,0x474100]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'refresh.elf'
    new_addr=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
         '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
         '-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
         '-Wl,-e,audio_uart_case_display_refresh_4abf86']
    cmd += [f'-Wl,--defsym={name}=0x{address:x}' for name,address in zip(NAMES,new_addr)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,wake,status,wear):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        calls=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new_addr],NAMES))
        results=dict(zip(NAMES,[wake,status,wear,0,0]))
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            calls.append(name)
            uc.reg_write(UC_ARM_REG_R0,results[name])
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x4abf86 if native else syms['audio_uart_case_display_refresh_4abf86']&~1
        u.emu_start(entry|1,0x130000,count=10000)
        return calls
    cases=0
    for wake in (0,1,2):
        for status in (0,1,2):
            for wear in (0,1,2):
                stock=run(True,wake,status,wear);rebuilt=run(False,wake,status,wear)
                if stock!=rebuilt:raise AssertionError((wake,status,wear,stock,rebuilt))
                cases+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_REFRESH_C','cases':cases,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'lower call order for bounded wake, case-status, and wear predicates',
         'remaining_gate':'Lower graphics actions and physical display effects require separate proof.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],cases,sha(OUT))

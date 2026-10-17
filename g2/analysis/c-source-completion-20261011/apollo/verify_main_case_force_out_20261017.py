#!/usr/bin/env python3
"""Bounded stock/C oracle for BoxDetect_SetForceOutBox 0x4ac5a2."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_force_out_4ac5a2_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-force-out/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_log_level','audio_log_extended','compressed_log_output',
       'audio_uart_case_force_out_apply_4ac798','audio_uart_case_display_refresh_4abf86',
       'audio_uart_case_notify_4abec8','audio_uart_display_housekeep',
       'audio_uart_case_force_out_finish_4ac19c']
STOCK_ADDR=[0x43d0ce,0x43d574,0x43ce9e,0x4ac798,0x4abf86,0x4abec8,0x47243a,0x4ac19c]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'force.elf'
    new_addr=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
         '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
         '-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
         '-Wl,-e,audio_uart_case_force_out_4ac5a2',
         '-Wl,--defsym=audio_uart_case_status_disabled=0x20075012']
    cmd += [f'-Wl,--defsym={name}=0x{address:x}' for name,address in zip(NAMES,new_addr)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,initial,value,flags):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(0x20075012,bytes((initial,)))
        effects=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new_addr],NAMES))
        def cstr(addr):return bytes(u.mem_read(addr,140)).split(b'\0')[0].decode('utf-8','replace')
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name=='audio_log_level':effects.append(('level',));uc.reg_write(UC_ARM_REG_R0,flags)
            elif name=='audio_log_extended':effects.append(('extended',r0,cstr(r1),cstr(r3)))
            elif name=='compressed_log_output':effects.append(('compact',r0,cstr(r1)))
            else:effects.append((name,r0 if name.endswith('4ac19c') else None))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_SP,0x200ff000)
        u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x4ac5a2 if native else syms['audio_uart_case_force_out_4ac5a2']&~1
        u.emu_start(entry|1,0x130000,count=20000)
        return bytes(u.mem_read(0x20075012,1)),effects
    cases=0
    for flags in (0,1,2,4,7):
        for initial in (0,1,255):
            for value in (0,1,255,256,257):
                stock=run(True,initial,value,flags)
                rebuilt=run(False,initial,value,flags)
                if stock!=rebuilt:raise AssertionError((initial,value,flags,stock,rebuilt))
                cases+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_FORCE_OUT_C','cases':cases,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'flag byte, lower call order and arguments, log level call order and codes for bounded flag values',
         'remaining_gate':'Five lower product calls and flag initializer remain separate source and placement contracts.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],cases,sha(OUT))

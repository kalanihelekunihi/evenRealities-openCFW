#!/usr/bin/env python3
"""Bounded stock/C oracle for Case nonce state update 0x4ac798."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_nonce_change_4ac798_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-nonce-change/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_uart_device_role_get','audio_uart_buffer_zero','audio_uart_service_nonce',
       'audio_uart_service_prepare3']
STOCK_ADDR=[0x45a568,0x43c0e4,0x4ac776,0x4ac828]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'nonce.elf';new_addr=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
         '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
         '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_case_force_out_apply_4ac798',
         '-Wl,--defsym=audio_uart_case_nonce_state_200036d8=0x200036d8']
    cmd += [f'-Wl,--defsym={name}=0x{address:x}' for name,address in zip(NAMES,new_addr)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,initial,nonce,role):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(0x200036d8,initial)
        calls=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new_addr],NAMES))
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            r0,r1,r2=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
            if name=='audio_uart_device_role_get':calls.append(('role',));uc.reg_write(UC_ARM_REG_R0,role)
            elif name=='audio_uart_buffer_zero':
                calls.append(('zero',r1,r2));uc.mem_write(r0,bytes(r1))
            elif name=='audio_uart_service_nonce':
                calls.append(('nonce',));uc.mem_write(r0,nonce);uc.reg_write(UC_ARM_REG_R0,0)
            else:calls.append(('prepare',r0))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x4ac798 if native else syms['audio_uart_case_force_out_apply_4ac798']&~1
        u.emu_start(entry|1,0x130000,count=12000)
        return bytes(u.mem_read(0x200036d8,4)),calls
    patterns=[bytes(x) for x in ((0,0,0,0),(1,2,3,4),(4,3,2,1),(255,0,255,0),(0,255,0,255))]
    cases=0
    for initial in patterns:
        for nonce in patterns:
            for role in (0,1,2):
                stock=run(True,initial,nonce,role);rebuilt=run(False,initial,nonce,role)
                if stock!=rebuilt:raise AssertionError((initial,nonce,role,stock,rebuilt))
                cases+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_NONCE_CHANGE_C','cases':cases,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'four-byte state and lower-call sequence for bounded state/nonce/role combinations',
         'remaining_gate':'Source ownership and initialization of persistent RAM 0x200036d8 remain open.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],cases,sha(OUT))

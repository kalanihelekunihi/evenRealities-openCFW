#!/usr/bin/env python3
"""Bounded stock/C packet and call oracle for Case status notification."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_notify_4abec8_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-notify/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_uart_buffer_zero','audio_uart_case_soc_4acaa0','audio_uart_case_charge_4acaac',
       'audio_uart_case_lid_4acab4','audio_uart_case_status','audio_log_level',
       'audio_log_extended','compressed_log_output','audio_ota_transfer_active',
       'audio_uart_case_send_status_510dec']
STOCK_ADDR=[0x43c0e4,0x4acaa0,0x4acaac,0x4acab4,0x4acad0,0x43d0ce,
            0x43d574,0x43ce9e,0x4487ac,0x510dec]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'notify.elf';new_addr=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
         '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
         '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_case_notify_4abec8']
    cmd += [f'-Wl,--defsym={name}=0x{address:x}' for name,address in zip(NAMES,new_addr)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,values,flags,transfer):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        calls=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new_addr],NAMES))
        result=dict(zip(NAMES,[0,*values,flags,0,0,transfer,0]))
        def cstr(addr):return bytes(u.mem_read(addr,150)).split(b'\0')[0].decode('utf-8','replace')
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name=='audio_uart_buffer_zero':
                calls.append(('zero',r1,r2));uc.mem_write(r0,bytes(r1))
            elif name in ('audio_uart_case_soc_4acaa0','audio_uart_case_charge_4acaac',
                          'audio_uart_case_lid_4acab4','audio_uart_case_status',
                          'audio_ota_transfer_active'):
                calls.append((name,));uc.reg_write(UC_ARM_REG_R0,result[name])
            elif name=='audio_log_level':calls.append(('level',));uc.reg_write(UC_ARM_REG_R0,flags)
            elif name=='audio_log_extended':calls.append(('extended',r0,cstr(r1),cstr(r3)))
            elif name=='compressed_log_output':calls.append(('compact',r0,cstr(r1)))
            else:calls.append(('send',r0,bytes(uc.mem_read(r1,5))))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x4abec8 if native else syms['audio_uart_case_notify_4abec8']&~1
        u.emu_start(entry|1,0x130000,count=20000)
        return calls
    patterns=[(0,0,0,0),(1,2,3,1),(255,128,64,2),(7,9,11,255)]
    cases=0
    for values in patterns:
        for flags in (0,1,2,4,7):
            for transfer in (0,1,2):
                stock=run(True,values,flags,transfer);rebuilt=run(False,values,flags,transfer)
                if stock!=rebuilt:raise AssertionError((values,flags,transfer,stock,rebuilt))
                cases+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_NOTIFY_C','cases':cases,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'five-byte packet, getter/log/send call order for bounded values, flags and transfer states',
         'remaining_gate':'Product status-row ownership and send provider 0x510dec remain open; physical transport untested.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],cases,sha(OUT))

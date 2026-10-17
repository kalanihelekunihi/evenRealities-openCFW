#!/usr/bin/env python3
"""Bounded stock/C oracle for Case info RX child 0x510bfe."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_rx_info_510bfe_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-rx-info/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_uart_checksum_copy','audio_ring_pb_assert_509b48','audio_log_level',
       'audio_log_extended','compressed_log_output']
STOCK_ADDR=[0x439c04,0x509b48,0x43d0ce,0x43d574,0x43ce9e]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'info.elf';new=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2',
         '-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-nostdlib',
         '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_case_rx_info_510bfe']
    cmd += [f'-Wl,--defsym={name}=0x{addr:x}' for name,addr in zip(NAMES,new)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,info,id_value,flags):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(0x20001000,b'12345678')
        effects=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new],NAMES))
        def cstr(a):return bytes(u.mem_read(a,180)).split(b'\0')[0].decode('utf-8','replace')
        def fault(a):
            raw=bytes(u.mem_read(a,20));return (int.from_bytes(raw[:4],'little'),
                int.from_bytes(raw[4:6],'little'),cstr(int.from_bytes(raw[8:12],'little')),
                cstr(int.from_bytes(raw[12:16],'little')),int.from_bytes(raw[16:20],'little'))
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name==NAMES[0]:effects.append(('copy',r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
            elif name==NAMES[1]:effects.append(('assert',fault(r0)))
            elif name==NAMES[2]:effects.append(('level',));uc.reg_write(UC_ARM_REG_R0,flags)
            elif name==NAMES[3]:effects.append(('extended',r0,cstr(r3)))
            else:effects.append(('compact',r0,cstr(r1)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_R0,id_value);u.reg_write(UC_ARM_REG_R1,0x20001000 if info else 0)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x510bfe if native else syms['audio_uart_case_rx_info_510bfe']&~1
        u.emu_start(entry|1,0x130000,count=2000)
        return u.reg_read(UC_ARM_REG_R0),effects
    count=0
    for info in (0,1):
     for id_value in (0,1,255,256):
      for flags in (0,1,2,4,7):
       args=(info,id_value,flags);stock=run(True,*args);rebuilt=run(False,*args)
       if stock!=rebuilt:raise AssertionError((args,stock,rebuilt))
       count+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_RX_INFO_C','cases':count,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'null/non-null result, fault record, lower call and log decisions',
         'remaining_gate':'Case info content semantics are handled by the decoded frame and downstream encoder.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],count,sha(OUT))

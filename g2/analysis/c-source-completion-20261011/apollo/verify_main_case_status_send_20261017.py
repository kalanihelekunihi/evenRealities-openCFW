#!/usr/bin/env python3
"""Bounded stock/C oracle for Case nanopb notification encoder 0x510dec."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_status_send_510dec_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-status-send/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_uart_display_area_copy_439c04','audio_ring_pb_assert_509b48',
       'audio_pb_ostream_from_buffer','audio_uart_buffer_zero','audio_pb_encode',
       'audio_ring_pb_tx_ble_475c1a','audio_log_level','audio_log_extended',
       'compressed_log_output']
STOCK_ADDR=[0x439c04,0x509b48,0x4905f4,0x43c0e4,0x490c32,0x475c1a,
            0x43d0ce,0x43d574,0x43ce9e]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'send.elf';new_addr=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
         '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
         '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_case_send_status_510dec',
         '-Wl,--defsym=audio_uart_case_tx_frame_200f5a9c=0x200f5a9c',
         '-Wl,--defsym=audio_uart_case_tx_encoded_2037c5a0=0x2037c5a0',
         '-Wl,--defsym=audio_uart_case_tx_magic_20074ffa=0x20074ffa',
         '-Wl,--defsym=audio_uart_case_descriptor_77793c=0x77793c']
    cmd += [f'-Wl,--defsym={name}=0x{address:x}' for name,address in zip(NAMES,new_addr)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,packet,magic,flags,encode_result):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000);u.mem_map(0x20370000,0x20000)
        u.mem_write(0x20074ffa,bytes((magic,)));u.mem_write(0x20082000,b'encode-error\0')
        if packet is not None:u.mem_write(0x20081000,packet)
        effects=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new_addr],NAMES))
        def word(v):return int.from_bytes(v,'little')
        def cstr(addr):return bytes(u.mem_read(addr,160)).split(b'\0')[0].decode('utf-8','replace') if addr else ''
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name=='audio_uart_display_area_copy_439c04':
                effects.append(('copy',r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
            elif name=='audio_ring_pb_assert_509b48':
                d=bytes(uc.mem_read(r0,20));effects.append(('assert',word(d[:4]),word(d[4:8]),
                    cstr(word(d[8:12])),cstr(word(d[12:16])),word(d[16:20])))
            elif name=='audio_pb_ostream_from_buffer':
                effects.append(('ostream',r1==0x2037c5a0,r2))
                data=(0x11111111).to_bytes(4,'little')+r1.to_bytes(4,'little')+r2.to_bytes(4,'little')+bytes(8)
                uc.mem_write(r0,data)
            elif name=='audio_uart_buffer_zero':
                effects.append(('zero',r1,r2));uc.mem_write(r0,bytes(r1))
            elif name=='audio_pb_encode':
                effects.append(('encode',r1==0x77793c,bytes(uc.mem_read(r2,10))))
                uc.mem_write(r0+12,(5).to_bytes(4,'little'))
                uc.mem_write(r0+16,(0x20082000).to_bytes(4,'little'))
                uc.mem_write(0x2037c5a0,b'abcde')
                uc.reg_write(UC_ARM_REG_R0,encode_result)
            elif name=='audio_ring_pb_tx_ble_475c1a':
                effects.append(('tx',r0,r1,r2==0x2037c5a0,r3))
            elif name=='audio_log_level':effects.append(('level',));uc.reg_write(UC_ARM_REG_R0,flags)
            elif name=='audio_log_extended':effects.append(('extended',r0,cstr(r1),cstr(r3)))
            elif name=='compressed_log_output':effects.append(('compact',r0,cstr(r1)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,0 if packet is None else 0x20081000)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x510dec if native else syms['audio_uart_case_send_status_510dec']&~1
        u.emu_start(entry|1,0x130000,count=30000)
        return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200f5a9c,10)),
                bytes(u.mem_read(0x20074ffa,1)),effects)
    cases=0
    for packet in (None,b'\x01\x02\x03\x04',b'\xff\x80\x00\x07'):
        for magic in (0,127,255):
            for flags in (0,1,2,4,7):
                for encode_result in (0,1,256):
                    stock=run(True,packet,magic,flags,encode_result)
                    rebuilt=run(False,packet,magic,flags,encode_result)
                    if stock!=rebuilt:raise AssertionError((packet,magic,flags,encode_result,stock,rebuilt))
                    cases+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_STATUS_SEND_C','cases':cases,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'return, frame bytes, magic and cut-call/log order across null, success and encode-failure inputs',
         'remaining_gate':'Product buffers, magic cell, descriptor, transport and hardware behavior remain separate contracts.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],cases,sha(OUT))

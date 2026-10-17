#!/usr/bin/env python3
"""Bounded stock/C oracle for Case nanopb RX dispatch 0x510a0c."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_sync_event_510a0c_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-sync-event/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
NAMES=['audio_uart_buffer_zero','audio_uart_pb_stream_init','audio_uart_checksum_copy',
       'audio_uart_pb_decode','audio_uart_case_rx_info_510bfe',
       'audio_uart_case_send_response_510c70','audio_log_level',
       'audio_log_extended','compressed_log_output']
STOCK_ADDR=[0x43c0e4,0x48f49c,0x439c04,0x490120,0x510bfe,0x510c70,
            0x43d0ce,0x43d574,0x43ce9e]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'sync.elf';new=[0x120001+i*0x20 for i in range(len(NAMES))]
    cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2',
         '-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-nostdlib',
         '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_case_sync_event_510a0c',
         '-Wl,--defsym=audio_uart_case_rx_frame_200f5a90=0x200f5a90',
         '-Wl,--defsym=audio_uart_case_descriptor_77793c=0x77793c']
    cmd += [f'-Wl,--defsym={name}=0x{addr:x}' for name,addr in zip(NAMES,new)]
    subprocess.run([*cmd,str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native,has_data,length,decoded,decode_ok,error_ptr,rx_result,tx_result,flags):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(0x200f5a90,b'\xaa'*10)
        u.mem_write(0x20001000,b'1234567890abcdef')
        u.mem_write(0x20002000,b'BAD_FRAME\0')
        effects=[];hooks=dict(zip(STOCK_ADDR if native else [x&~1 for x in new],NAMES))
        def cstr(a):return bytes(u.mem_read(a,180)).split(b'\0')[0].decode('utf-8','replace')
        def hook(uc,addr,size,_):
            name=hooks.get(addr)
            if name is None:return
            r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name==NAMES[0]:effects.append(('zero',r1,r2));uc.mem_write(r0,bytes((r2&255,))*r1)
            elif name==NAMES[1]:
                effects.append(('stream',r1,r2))
                uc.mem_write(r0,(0x48f3a5).to_bytes(4,'little')+r1.to_bytes(4,'little')+r2.to_bytes(4,'little')+bytes(4))
            elif name==NAMES[2]:effects.append(('copy',r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
            elif name==NAMES[3]:
                effects.append(('decode',bytes(uc.mem_read(r0,16))))
                uc.mem_write(r2,decoded)
                uc.mem_write(r0+12,(0x20002000 if error_ptr else 0).to_bytes(4,'little'))
                uc.reg_write(UC_ARM_REG_R0,decode_ok)
            elif name==NAMES[4]:effects.append(('rx',r0,bytes(uc.mem_read(r1,5))));uc.reg_write(UC_ARM_REG_R0,rx_result)
            elif name==NAMES[5]:effects.append(('tx',r0,bytes(uc.mem_read(r1,5))));uc.reg_write(UC_ARM_REG_R0,tx_result)
            elif name==NAMES[6]:effects.append(('level',));uc.reg_write(UC_ARM_REG_R0,flags)
            elif name==NAMES[7]:
                sp=uc.reg_read(UC_ARM_REG_SP)
                msg=cstr(int.from_bytes(uc.mem_read(sp+4,4),'little'))
                effects.append(('extended',r0,msg))
            else:effects.append(('compact',r0,cstr(r1)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_R0,0x20001000 if has_data else 0)
        u.reg_write(UC_ARM_REG_R1,length)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x510a0c if native else syms['audio_uart_case_sync_event_510a0c']&~1
        u.emu_start(entry|1,0x130000,count=30000)
        return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200f5a90,10)),effects)
    count=0
    decoded_values=[bytes((cmd,typ,0,0,1,2,3,4,5,6)) for cmd in (0,1,2,255) for typ in (0,1,4)]
    for has_data in (0,1):
     for length in (0,1,8,255,256,65535,65536):
      for decoded in decoded_values:
       for decode_ok,error_ptr,rx_result,tx_result,flags in [
         (0,0,0,0,0),(0,1,0,0,7),
         (1,0,0,0,0),(1,0,0,43,7),
         (1,0,1,0,2),(1,0,2,0,1)]:
        args=(has_data,length,decoded,decode_ok,error_ptr,rx_result,tx_result,flags)
        stock=run(True,*args);rebuilt=run(False,*args)
        if stock!=rebuilt:raise AssertionError((args,stock,rebuilt))
        count+=1
    rec={'status':'PASS_BOUNDED_MAIN_CASE_SYNC_EVENT_C','cases':count,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'RX frame zero/decode, command dispatch, lower call order, return codes and logging decisions over bounded input/state',
         'remaining_gate':'Decoded Case info handler 0x510bfe, response encoder 0x510c70, and 10-byte RX frame storage remain.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],count,sha(OUT))

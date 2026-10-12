"""Actual compiled ARM C/native LV filesystem lookup and bind cases."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_fs_registry_bind.c'
SHIM='''#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x200];
void *audio_uart_lv_list_first(void*a){(void)a;return 0;}
void *audio_uart_lv_list_next(void*a,void*b){(void)a;(void)b;return 0;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_fs_driver_find_4c70b4',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for function in ('find','bind'):
        for found in (0,1,2) if function=='find' else (1,2):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                root=syms['audio_uart_display_lv_root'] if is_c else 0x2006f548
                slot1=0x20002000;slot2=0x20002100
                drv1=0x20003000;drv2=0x20003100
                u.mem_write(slot1,struct.pack('<I',drv1));u.mem_write(slot2,struct.pack('<I',drv2))
                u.mem_write(drv1,bytes([0x4c if found==1 else 0x58]))
                u.mem_write(drv2,bytes([0x4c if found==2 else 0x59]))
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,0x4c if function=='find' else 0x20004000)
                first=(syms['audio_uart_lv_list_first']&~1) if is_c else 0x482cd8
                nxt=(syms['audio_uart_lv_list_next']&~1) if is_c else 0x482cf0
                calls=[]
                def hook(uc,a,size,_):
                    if a==first:
                        calls.append(('first',uc.reg_read(UC_ARM_REG_R0)==root+0x180))
                        uc.reg_write(UC_ARM_REG_R0,slot1)
                    elif a==nxt:
                        cur=uc.reg_read(UC_ARM_REG_R1)
                        calls.append(('next',uc.reg_read(UC_ARM_REG_R0)==root+0x180,cur))
                        uc.reg_write(UC_ARM_REG_R0,slot2 if cur==slot1 else 0)
                    else:return
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                start=(syms['audio_uart_lv_fs_driver_find_4c70b4'] if is_c else 0x4c70b4) if function=='find' else (syms['audio_uart_lv_init_global_bind_4c8efc'] if is_c else 0x4c8efc)
                u.emu_start(start|1,0x600000,count=120)
                result=u.reg_read(UC_ARM_REG_R0) if function=='find' else 0
                traces.append((result,calls,bytes(u.mem_read(drv1+0x30,4)),bytes(u.mem_read(drv2+0x30,4))))
            assert traces[0]==traces[1],(function,found,traces)
    print('PASS 5 compiled-C/native LV filesystem registry cases')

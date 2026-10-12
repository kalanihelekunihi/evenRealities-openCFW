"""Actual compiled ARM C/native LV FS construct/register effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_fs_driver_register.c'
SHIM='''#include <stdint.h>
#include <stddef.h>
uint8_t audio_uart_display_lv_root[0x200];
void *memset(void*a,int b,size_t c){(void)b;(void)c;return a;}
void *audio_uart_lv_list_prepend_482b12(uint32_t*a){(void)a;return 0;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...)
{(void)a;(void)b;(void)c;(void)d;}'''
FUNCS={'construct':(0x4c7064,'audio_uart_lv_fs_driver_construct_4c7064'),
       'register':(0x4c706e,'audio_uart_lv_fs_driver_register_4c706e')}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_fs_driver_construct_4c7064',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for name,(native,csym) in FUNCS.items():
        for success in ((False,True) if name=='register' else (True,)):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                root=syms['audio_uart_display_lv_root'] if is_c else 0x2006f548
                driver=0x20003000;slot=0x20002000
                u.mem_write(driver,b'\xa5'*52);u.mem_write(slot,b'\xa5'*4)
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,driver)
                zero=(syms['memset']&~1) if is_c else 0x4c6d80
                prepend=(syms['audio_uart_lv_list_prepend_482b12']&~1) if is_c else 0x482b12
                log=(syms['audio_uart_lvgl_log']&~1) if is_c else 0x44d25c
                calls=[];faults=[]
                def hook(uc,a,size,_):
                    if a==zero:
                        length=uc.reg_read(UC_ARM_REG_R2) if is_c else uc.reg_read(UC_ARM_REG_R1)
                        calls.append(('zero',length));uc.mem_write(driver,b'\x00'*length)
                        uc.reg_write(UC_ARM_REG_R0,driver)
                    elif a==prepend:
                        calls.append(('prepend',uc.reg_read(UC_ARM_REG_R0)==root+0x180))
                        uc.reg_write(UC_ARM_REG_R0,slot if success else 0)
                    elif a==log:
                        calls.append(('log',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R2)))
                    else:return
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                def bad(uc,access,address,size,value,_):
                    faults.append((address,size,value));uc.emu_stop();return False
                u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,bad)
                try:u.emu_start((syms[csym] if is_c else native)|1,0x600000,count=120)
                except Exception:
                    if not faults:raise
                traces.append((calls,bytes(u.mem_read(driver,52)),bytes(u.mem_read(slot,4)),faults))
            assert traces[0]==traces[1],(name,success,traces)
    print('PASS 3 compiled-C/native LV FS driver construct/register cases')

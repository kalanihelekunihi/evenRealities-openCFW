"""Actual compiled ARM C/native LV FS descriptor callback identities/order."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_fs_driver_init.c'
CALLBACKS={0x0c:0x4c8f58,0x10:0x4c8fd8,0x14:0x4c8ff0,0x18:0x4c900c,
           0x1c:0x4c9028,0x20:0x4c9064,0x24:0x4c9080,0x28:0x4c9104,0x2c:0x4c90e4}
SHIM='''#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x200];
void audio_uart_lv_fs_driver_construct_4c7064(void*a){(void)a;}
void audio_uart_lv_fs_driver_register_4c706e(void*a){(void)a;}\n'''
for a in CALLBACKS.values():SHIM+='void audio_uart_lv_fs_'+{
 0x4c8f58:'open',0x4c8fd8:'close',0x4c8ff0:'read',0x4c900c:'write',
 0x4c9028:'seek',0x4c9064:'tell',0x4c9080:'dir_open',
 0x4c9104:'dir_read',0x4c90e4:'dir_close'}[a]+'_'+hex(a)[2:]+'(void){}\n'
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_init_misc_4c8f0a',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    traces=[]
    for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        root=syms['audio_uart_display_lv_root'] if is_c else 0x2006f548
        driver=root+0x18c;u.mem_write(driver,b'\xa5'*0x34)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        construct=(syms['audio_uart_lv_fs_driver_construct_4c7064']&~1) if is_c else 0x4c7064
        register=(syms['audio_uart_lv_fs_driver_register_4c706e']&~1) if is_c else 0x4c706e
        calls=[]
        def hook(uc,a,size,_):
            if a==construct:calls.append(('construct',uc.reg_read(UC_ARM_REG_R0)==driver))
            elif a==register:calls.append(('register',uc.reg_read(UC_ARM_REG_R0)==driver))
            else:return
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        start=syms['audio_uart_lv_init_misc_4c8f0a'] if is_c else 0x4c8f0a
        u.emu_start(start|1,0x600000,count=100)
        callback_matches=[]
        for offset,a in CALLBACKS.items():
            label={0x4c8f58:'open',0x4c8fd8:'close',0x4c8ff0:'read',0x4c900c:'write',
              0x4c9028:'seek',0x4c9064:'tell',0x4c9080:'dir_open',
              0x4c9104:'dir_read',0x4c90e4:'dir_close'}[a]
            expected=syms['audio_uart_lv_fs_'+label+'_'+hex(a)[2:]] if is_c else a
            actual=struct.unpack('<I',u.mem_read(driver+offset,4))[0]
            callback_matches.append((offset,(actual&~1)==(expected&~1)))
        traces.append((calls,bytes(u.mem_read(driver,1)),callback_matches))
    assert traces[0]==traces[1],traces
    assert all(match for _,match in traces[0][2]),traces[0]
    print('PASS compiled-C/native LV FS driver descriptor callback table')

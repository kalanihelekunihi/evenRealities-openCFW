"""Actual compiled ARM C/native 0x45f7be ordered release and state effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_audio_release.c'
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_unlink_450500(void*a,void*b){(void)a;(void)b;return 0;}
void audio_uart_display_event_remove_callback(void*a,void(*b)(void)){(void)a;(void)b;}
void audio_uart_page_event_45f914(void){}
void audio_uart_display_page_deinit(void*a){(void)a;}
void audio_uart_display_object_delete(void*a){(void)a;}
void audio_file_heap_free(void*a){(void)a;}
void audio_uart_display_audio_finalize(void){}'''
NATIVE={'anim':0x450500,'event':0x451862,'page':0x45fbae,
        'object':0x44d7b8,'free':0x474d16,'finish':0x45bbd2}
NAMES={'anim':'audio_uart_lv_style_unlink_450500',
       'event':'audio_uart_display_event_remove_callback',
       'page':'audio_uart_display_page_deinit',
       'object':'audio_uart_display_object_delete','free':'audio_file_heap_free',
       'finish':'audio_uart_display_audio_finalize'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_audio_release',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for scenario in ('null','empty','first','both'):
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            base=0x20001000
            u.mem_write(base,b'\xa5'*256)
            u.mem_write(base+24,struct.pack('<I',0x20004000))
            if scenario in ('first','both'):
                u.mem_write(base+8,struct.pack('<I',0x20002000))
                u.mem_write(0x20002004,struct.pack('<I',0x20005000))
                u.mem_write(0x20002020,struct.pack('<I',0x20002100))
                u.mem_write(0x20002104,struct.pack('<I',0x20005100))
            else:u.mem_write(base+8,struct.pack('<I',0))
            if scenario=='both':
                u.mem_write(base+12,struct.pack('<I',0x20002200))
                u.mem_write(0x20002204,struct.pack('<I',0x20005200))
            else:u.mem_write(base+12,struct.pack('<I',0))
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,0 if scenario=='null' else base)
            mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0)
                if n=='event':calls.append((n,r0,'callback'))
                elif n=='anim':calls.append((n,r0,uc.reg_read(UC_ARM_REG_R1)))
                else:calls.append((n,r0 if n!='finish' else None))
                uc.reg_write(UC_ARM_REG_R0,0)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['audio_uart_display_audio_release'] if is_c else 0x45f7be
            u.emu_start(start|1,0x600000,count=250)
            traces.append((calls,bytes(u.mem_read(base,256))))
        assert traces[0]==traces[1],(scenario,traces[0][0],traces[1][0])
    print('PASS 4 compiled-C/native display audio release list cases')

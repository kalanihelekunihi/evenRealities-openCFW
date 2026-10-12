"""Actual compiled ARM C/native LV startup child calls and array fields."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
DIR=ROOT/'components/audio/uart_thread_source_candidate'
FUNCS={'memory':(0x48aa60,'audio_uart_lv_init_memory_48aa60'),
       'async':(0x49acb0,'audio_uart_lv_init_async_49acb0'),
       'display':(0x464330,'audio_uart_lv_init_display_464330'),
       'indev':(0x4c6d8c,'audio_uart_lv_init_indev_4c6d8c'),
       'style':(0x44d32c,'audio_uart_lv_init_style_44d32c'),
       'anim':(0x48438c,'audio_uart_lv_init_anim_48438c'),
       'cache':(0x44b90c,'audio_uart_lv_init_cache_44b90c'),
       'image_decoder':(0x488f4c,'audio_uart_lv_image_decoder_init_488f4c')}
LOWERS={'handlers':(0x48aa80,'audio_uart_lv_draw_handlers_default_48aa80'),
        'async':(0x4d465c,'audio_uart_lv_async_init_4d465c'),
        'display':(0x4645d8,'audio_uart_lv_display_init_4645d8'),
        'anim':(0x4d46de,'audio_uart_lv_anim_init_4d46de'),
        'image_cache_init':(0x4d4ad4,'audio_uart_lv_image_cache_init_4d4ad4'),
        'header_cache_init':(0x4d4bdc,'audio_uart_lv_image_header_cache_init_4d4bdc')}
SHIM='''#include <stdint.h>
#include <stddef.h>
uint8_t audio_uart_display_lv_root[0x200];
void *memset(void*p,int c,size_t n){(void)c;(void)n;return p;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...)
{(void)a;(void)b;(void)c;(void)d;}\n'''
for _,name in LOWERS.values():SHIM+='void '+name+'(){}\n'
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    # Isolate the eight startup children; appended providers are independently qualified.
    children=Path(td)/'children.c'
    children.write_text((DIR/'display_lv_init_children.c').read_text().split('/* Full native4c6d04..4c6d62:')[0])
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_init_memory_48aa60',
                    str(children),str(DIR/'display_lv_global_init.c'),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for group,(native,csym) in FUNCS.items():
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            root=syms['audio_uart_display_lv_root'] if is_c else 0x2006f548
            u.mem_write(root,b'\xa5'*0x200)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,0x111);u.reg_write(UC_ARM_REG_R1,0x222)
            mapping={((syms[sym]&~1) if is_c else a):n for n,(a,sym) in LOWERS.items()}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                n=mapping[a];arg=uc.reg_read(UC_ARM_REG_R0)
                calls.append((n,arg-root if n in ('handlers','async','anim') else arg))
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.emu_start((syms[csym] if is_c else native)|1,0x600000,count=100)
            traces.append((calls,bytes(u.mem_read(root,0x200))))
        assert traces[0]==traces[1],(group,traces[0][0],traces[1][0])
    print('PASS 8 compiled-C/native LV startup child cases')

"""Bounded original-byte / compiled-C glyph cache initializer comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
NATIVE={'audio_uart_lv_lock_core':0x4d4666,'audio_uart_lv_unlock_core':0x4d4696,
 'audio_uart_font_get_char_index':0x526f10,'audio_uart_font_face_load_scalable':0x526d54,
 'audio_uart_font_face_select_size':0x526ca8,'audio_uart_font_load_glyph':0x525574,
 'audio_uart_font_italic_shift':0x4b201e,'audio_uart_lvgl_log':0x44d25c}
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_lock_core(void*p){(void)p;return 0;}
uint32_t audio_uart_lv_unlock_core(void*p){(void)p;return 0;}
uint32_t audio_uart_font_get_char_index(void*p,uint32_t n){(void)p;(void)n;return 3;}
int32_t audio_uart_font_face_load_scalable(void*p,uint32_t a,uint32_t b){(void)p;(void)a;(void)b;return 0;}
int32_t audio_uart_font_face_select_size(void*p,uint32_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_font_load_glyph(void*p,uint32_t n,uint32_t f){(void)p;(void)n;(void)f;return 0;}
int16_t audio_uart_font_italic_shift(uint16_t a,uint16_t b){(void)a;(void)b;return 7;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}
'''
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'shim.c';shim.write_text(SHIM)
    elf=Path(d)/'glyph.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
        '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_glyph_cache_initialize',
        str(ROOT/'components/audio/uart_thread_source_candidate/display_font_glyph_initialize.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    ENTRY=0x20010000;FONT=0x20010100;CONTEXT=0x20010200;FACE=0x20010300;SLOT=0x20010400
    def setword(u,addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
    def fixture(u,mode,style):
        setword(u,ENTRY,65);setword(u,FONT+0x34,CONTEXT);setword(u,FONT+0x28,12)
        u.mem_write(FONT+0x2d,bytes([mode]));u.mem_write(FONT+0x2c,bytes([style]))
        setword(u,CONTEXT+0xc,FACE);u.mem_write(FACE+8,b'\x01');setword(u,FACE+0x54,SLOT)
        for offset,value in {0x18:128,0x1c:256,0x20:192,0x24:320,0x28:384,0x40:448,
                             0x4c:11,0x50:13,0x64:17,0x68:23,0x48:0x62697473}.items():
            setword(u,SLOT+offset,value)
    def run(compiled,mode,style,failure):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        fixture(u,mode,style)
        calls=[]
        targets={((symbols[n] if compiled else addr)&~1):n for n,addr in NATIVE.items()}
        def intercept(uc,address,size,user):
            name=targets.get(address)
            if name is None:return
            arity={'audio_uart_lv_lock_core':1,'audio_uart_lv_unlock_core':1,'audio_uart_font_get_char_index':2,'audio_uart_font_face_load_scalable':3,'audio_uart_font_face_select_size':2,'audio_uart_font_load_glyph':3,'audio_uart_font_italic_shift':2,'audio_uart_lvgl_log':0}[name]
            calls.append((name,(uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2))[:arity]))
            value=3 if name=='audio_uart_font_get_char_index' else 7 if name=='audio_uart_font_italic_shift' else 0
            if failure==name:value=0x17
            uc.reg_write(UC_ARM_REG_R0,value)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,intercept)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,ENTRY);u.reg_write(UC_ARM_REG_R1,FONT)
        address=symbols['audio_uart_font_glyph_cache_initialize'] if compiled else 0x5295a8
        u.emu_start(address|1,0x600000,count=20000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(ENTRY,0x24)),calls
    for mode,style,failure in [(1,0,None),(1,1,None),(0,0,None),(2,0,None),
                               (1,0,'audio_uart_font_face_load_scalable'),
                               (1,0,'audio_uart_font_load_glyph')]:
        a=run(False,mode,style,failure);b=run(True,mode,style,failure)
        assert a==b,(mode,style,failure,a,b)
        print('PASS',mode,style,failure)

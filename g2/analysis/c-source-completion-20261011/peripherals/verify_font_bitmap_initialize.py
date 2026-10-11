"""Bounded native/compiled C bitmap-cache initializer comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
NATIVE={'audio_uart_lv_lock_core':0x4d4666,'audio_uart_lv_unlock_core':0x4d4696,
 'audio_uart_font_face_load_scalable':0x526d54,'audio_uart_font_face_select_size':0x526ca8,
 'audio_uart_font_load_glyph':0x525574,'audio_uart_font_render_glyph':0x527228,
 'audio_uart_font_get_glyph':0x567ec8,'audio_uart_font_done_glyph':0x567f88,
 'audio_uart_font_bitmap_stride':0x48aad8,'audio_uart_font_bitmap_allocate':0x48b010,
 'audio_uart_checksum_copy':0x454738,'audio_uart_lvgl_log':0x44d25c}
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_lock_core(void*p){(void)p;return 0;}
uint32_t audio_uart_lv_unlock_core(void*p){(void)p;return 0;}
int32_t audio_uart_font_face_load_scalable(void*p,uint32_t a,uint32_t b){(void)p;(void)a;(void)b;return 0;}
int32_t audio_uart_font_face_select_size(void*p,uint32_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_font_load_glyph(void*p,uint32_t n,uint32_t f){(void)p;(void)n;(void)f;return 0;}
int32_t audio_uart_font_render_glyph(void*p,uint32_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_font_get_glyph(void*p,void**out){(void)p;(void)out;return 0;}
void audio_uart_font_done_glyph(void*p){(void)p;}
uint32_t audio_uart_font_bitmap_stride(uint16_t w,uint8_t f){(void)w;(void)f;return 4;}
void* audio_uart_font_bitmap_allocate(void*p,uint16_t w,uint16_t h,uint8_t f,uint32_t s){(void)p;(void)w;(void)h;(void)f;(void)s;return (void*)0x20010600;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}
uint8_t audio_uart_display_lv_state[0x400];
'''
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'shim.c';shim.write_text(SHIM)
    elf=Path(d)/'bitmap.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
        '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_bitmap_cache_initialize',
        str(ROOT/'components/audio/uart_thread_source_candidate/display_font_bitmap_initialize.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    ENTRY=0x20010000;FONT=0x20010100;CONTEXT=0x20010200;FACE=0x20010300;SLOT=0x20010400
    GLYPH=0x20010500;BUFFER=0x20010600;DATA=0x20010700;SOURCE=0x20010800
    def setword(u,addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
    def fixture(u):
        setword(u,ENTRY,3);setword(u,FONT+0x34,CONTEXT);setword(u,FONT+0x28,12)
        setword(u,CONTEXT+0xc,FACE);u.mem_write(FACE+8,b'\x01');setword(u,FACE+0x54,SLOT)
        setword(u,GLYPH+0x1c,2);setword(u,GLYPH+0x20,3);setword(u,GLYPH+0x24,3)
        setword(u,GLYPH+0x28,SOURCE);u.mem_write(GLYPH+0x2e,b'\x07')
        setword(u,BUFFER+0x10,DATA);u.mem_write(SOURCE,b'ABCDEF')
    def run(compiled,failure):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        fixture(u)
        calls=[]
        targets={((symbols[n] if compiled else addr)&~1):n for n,addr in NATIVE.items()}
        arity={'audio_uart_lv_lock_core':1,'audio_uart_lv_unlock_core':1,
            'audio_uart_font_face_load_scalable':3,'audio_uart_font_face_select_size':2,
            'audio_uart_font_load_glyph':3,'audio_uart_font_render_glyph':2,
            'audio_uart_font_get_glyph':2,'audio_uart_font_done_glyph':1,
            'audio_uart_font_bitmap_stride':2,'audio_uart_font_bitmap_allocate':4,
            'audio_uart_checksum_copy':3,'audio_uart_lvgl_log':0}
        def intercept(uc,address,size,user):
            name=targets.get(address)
            if name is None:return
            args=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name=='audio_uart_font_bitmap_allocate':
                assert args[0]==(symbols['audio_uart_display_lv_state']+0xe8 if compiled else 0x2006f630)
                calls.append((name,('product-cell',)+args[1:arity[name]]))
            else:calls.append((name,args[:arity[name]]))
            value=0x17 if failure==name else 0
            if name=='audio_uart_font_get_glyph' and failure!=name:uc.mem_write(args[1],struct.pack('<I',GLYPH))
            if name=='audio_uart_font_bitmap_stride':value=4
            if name=='audio_uart_font_bitmap_allocate':value=BUFFER
            if name=='audio_uart_checksum_copy' and failure!=name:
                uc.mem_write(args[0],bytes(uc.mem_read(args[1],args[2])))
            uc.reg_write(UC_ARM_REG_R0,value)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,intercept)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,ENTRY);u.reg_write(UC_ARM_REG_R1,FONT)
        address=symbols['audio_uart_font_bitmap_cache_initialize'] if compiled else 0x529936
        u.emu_start(address|1,0x600000,count=20000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(ENTRY,12)),bytes(u.mem_read(DATA,12)),calls
    for failure in (None,'audio_uart_font_face_load_scalable','audio_uart_font_load_glyph',
                    'audio_uart_font_render_glyph','audio_uart_font_get_glyph'):
        a=run(False,failure);b=run(True,failure)
        assert a==b,(failure,a,b)
        print('PASS',failure)

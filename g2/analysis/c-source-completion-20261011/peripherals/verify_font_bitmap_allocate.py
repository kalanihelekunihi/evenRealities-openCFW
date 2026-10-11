"""Stock versus actual C draw-buffer allocation with controlled allocator callbacks."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
DEV=0x20010000;OUT=0x20011000;PIX=0x20012000;STATE=0x2006f548
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c'
    shim.write_text('''__attribute__((naked,used)) void *audio_uart_lv_heap_alloc(unsigned n){__asm__ volatile("bx lr");}
__attribute__((naked,used)) void audio_uart_lv_heap_free(void *p){__asm__ volatile("bx lr");}
__attribute__((naked,used)) unsigned audio_uart_font_bitmap_stride(unsigned w,unsigned f){__asm__ volatile("bx lr");}
__attribute__((naked,used)) void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,const char*e,...){__asm__ volatile("bx lr");}
''')
    elf=Path(td)/'a.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_bitmap_allocate','-Wl,--defsym,audio_uart_display_lv_state=0x2006f548',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_bitmap_allocate.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f: segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,fmt):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(OUT,b'\0'*28)
        u.mem_write(DEV,struct.pack('<I',0x20020001));u.mem_write(STATE+0xc8+8,struct.pack('<I',0x20020011))
        trace=[];hooks={0x20020000:'pixel',0x20020010:'palette',(syms['audio_uart_lv_heap_alloc']&~1) if candidate else 0x44f730:'heap'}
        def hook(u,pc,size,_):
            op=hooks.get(pc)
            if op is None:return
            r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
            trace.append((op,r0,r1))
            u.reg_write(UC_ARM_REG_R0,{'pixel':PIX,'palette':PIX+16,'heap':OUT}[op]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,DEV);u.reg_write(UC_ARM_REG_R1,13);u.reg_write(UC_ARM_REG_R2,7);u.reg_write(UC_ARM_REG_R3,fmt)
        u.mem_write(0x200ff000,struct.pack('<I',16))
        u.emu_start((syms['audio_uart_font_bitmap_allocate'] if candidate else 0x48b010)|1,0x600000,count=20000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(OUT,28))
    for fmt in [0x0e,7,8,9,10,20]:
        a=run(False,fmt);b=run(True,fmt)
        assert a==b,(fmt,a,b)
        print('PASS bitmap allocate',fmt)

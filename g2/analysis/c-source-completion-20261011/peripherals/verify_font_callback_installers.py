"""Native versus compiled C callback installer pointer roles on valid descriptors."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callbacks=[('audio_uart_font_cb_glyph',0x529460),('audio_uart_font_cb_bitmap_glyph',0x529858),('audio_uart_font_cb_bitmap_draw',0x5298f8),('audio_uart_font_cb_outline_glyph',0x529d70),('audio_uart_font_cb_outline_draw',0x529e04)]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'shims.c';shim.write_text(''.join('__attribute__((naked,used)) void '+n+'(void){__asm__ volatile("bx lr");}\n' for n,_ in callbacks)+'void audio_uart_lvgl_log(unsigned a,const char *b,unsigned c,const char *d,const char *e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}')
    elf=Path(d)/'installers.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_callbacks_common',
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_callback_installers.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    tests=[('common',0x529406,'audio_uart_font_callbacks_common'),('bitmap',0x5297f8,'audio_uart_font_callbacks_bitmap'),('outline',0x529b7e,'audio_uart_font_callbacks_outline')]
    mapping={original|1:symbols[name]|1 for name,original in callbacks}
    def run(compiled,stock,name):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);desc=0x20010000
        u.mem_write(desc,struct.pack('<IIII',0x5f5f4654,0xaaaaaaaa,0xbbbbbbbb,0xcccccccc))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,desc)
        u.emu_start((symbols[name] if compiled else stock)|1,0x600000,count=5000)
        values=struct.unpack('<IIII',u.mem_read(desc,16))
        return tuple(mapping.get(x,x) for x in values) if not compiled else values
    for label,stock,name in tests:
        a=run(False,stock,name);b=run(True,stock,name)
        assert a==b,(label,a,b)
        print('PASS',label,[hex(x) for x in a])

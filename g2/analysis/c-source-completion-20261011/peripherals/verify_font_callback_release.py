"""Native/compiled-C bitmap and outline callback cache release transitions."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'shims.c';shim.write_text('__attribute__((naked,used)) void audio_uart_font_cache_remove(void){__asm__ volatile("bx lr");}\nvoid audio_uart_lvgl_log(unsigned a,const char *b,unsigned c,const char *d,const char *e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}')
    elf=Path(d)/'release.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_cb_bitmap_draw',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_callback_release.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    FONT=0x20010000;DESC=0x20010100;CTX=0x20010200;DRAW=0x20010300;CACHE=0x20010400;NODE=0x20010500
    def run(compiled,kind,node):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(FONT+0x18,struct.pack('<I',DESC));u.mem_write(DESC+0x34,struct.pack('<I',CTX));u.mem_write(CTX+0x1c,struct.pack('<I',CACHE));u.mem_write(DRAW+0x1c,struct.pack('<I',node))
        trace=[];hook_addr=(symbols['audio_uart_font_cache_remove']&~1) if compiled else 0x4d4e72
        def hook(u,addr,size,_):
            if addr==hook_addr:
                trace.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)))
                u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,FONT);u.reg_write(UC_ARM_REG_R1,DRAW)
        native=0x5298f8 if kind=='bitmap' else 0x529e04
        symbol='audio_uart_font_cb_bitmap_draw' if kind=='bitmap' else 'audio_uart_font_cb_outline_draw'
        u.emu_start((symbols[symbol] if compiled else native)|1,0x600000,count=10000)
        return trace,struct.unpack('<I',u.mem_read(DRAW+0x1c,4))[0]
    for kind in ('bitmap','outline'):
      for node in (0,NODE):
        a=run(False,kind,node);b=run(True,kind,node)
        assert a==b,(kind,node,a,b)
        print('PASS',kind,hex(node),a)

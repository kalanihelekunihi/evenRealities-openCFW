"""Stock/compiled-C cubic border append with controlled grow outcome."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'grow.c';shim.write_text('__attribute__((naked,used)) void audio_uart_font_stroker_border_grow(void){__asm__ volatile("bx lr");}')
    elf=Path(d)/'cubic.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_border_cubic',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_border_cubic.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    B=0x20010000;P=B+0x100;T=B+0x200;A=B+0x300;C=B+0x308;E=B+0x310
    def run(compiled,count,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(B,b'\0'*0x400)
        u.mem_write(B,struct.pack('<I',count));u.mem_write(B+8,struct.pack('<II',P,T));u.mem_write(B+16,b'\x01')
        for ptr,xy in ((A,(11,22)),(C,(33,44)),(E,(55,66))):u.mem_write(ptr,struct.pack('<ii',*xy))
        trace=[];grow=(syms['audio_uart_font_stroker_border_grow']&~1) if compiled else 0x5682de
        def hook(u,pc,size,_):
            if pc!=grow:return
            trace.append((u.reg_read(UC_ARM_REG_R0)-B,u.reg_read(UC_ARM_REG_R1)))
            u.reg_write(UC_ARM_REG_R0,7 if fail else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,B);u.reg_write(UC_ARM_REG_R1,A);u.reg_write(UC_ARM_REG_R2,C);u.reg_write(UC_ARM_REG_R3,E)
        u.emu_start((syms['audio_uart_font_stroker_border_cubic'] if compiled else 0x5684c2)|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(B,0x20)),bytes(u.mem_read(P,0x90)),bytes(u.mem_read(T,0x10))
    for case in [(0,False),(0,True),(1,False),(1,True),(5,False),(5,True)]:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b);print('PASS border cubic',case)

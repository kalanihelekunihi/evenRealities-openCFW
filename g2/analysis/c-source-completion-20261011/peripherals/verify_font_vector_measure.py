"""Compiled-C/stock vector angle and length with controlled angle core."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'angle.c';shim.write_text('__attribute__((naked,used)) void audio_uart_font_vector_angle_core(void){__asm__ volatile("bx lr");}')
    src=ROOT/'components/audio/uart_thread_source_candidate'
    elf=Path(d)/'measure.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_vector_angle',str(src/'display_font_freetype_vector_measure.c'),str(src/'display_font_freetype_rotate_scalars.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    V=0x20010000
    def run(compiled,kind,x,y):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(V,struct.pack('<ii',x,y))
        trace=[];core=(syms['audio_uart_font_vector_angle_core']&~1) if compiled else 0x528ee4
        def hook(u,pc,size,_):
            if pc!=core:return
            p=u.reg_read(UC_ARM_REG_R0);a,b=struct.unpack('<ii',u.mem_read(p,8));trace.append((a,b))
            u.mem_write(p,struct.pack('<ii',0x28000000,0x123450));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if kind=='angle':u.reg_write(UC_ARM_REG_R0,x&0xffffffff);u.reg_write(UC_ARM_REG_R1,y&0xffffffff);addr=0x528fbc;sym='audio_uart_font_vector_angle'
        else:u.reg_write(UC_ARM_REG_R0,V);addr=0x529086;sym='audio_uart_font_vector_length'
        u.emu_start((syms[sym] if compiled else addr)|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0),trace
    cases=[(0,0),(0,100),(0,-100),(100,0),(-100,0),(100,200),(-100,200),(123456,-654321),(0x70000000,0x10000000)]
    for kind in ('angle','length'):
        for x,y in cases:
            a=run(False,kind,x,y);b=run(True,kind,x,y);assert a==b,(kind,x,y,a,b);print('PASS measure',kind,x,y)

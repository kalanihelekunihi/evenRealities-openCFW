"""Bounded compiled-C/stock border move comparison with real selected close."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'add.c';shim.write_text(''.join('__attribute__((naked,used)) void '+n+'(void){__asm__ volatile("bx lr");}' for n in ('audio_uart_font_stroker_border_add','audio_uart_font_stroker_border_close')))
    src=ROOT/'components/audio/uart_thread_source_candidate'
    elf=Path(d)/'move.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_border_move',str(src/'display_font_freetype_stroker_border_move.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    S=0x20010000;P=S+0x100
    def run(compiled,start,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(S,b'\0'*0x200)
        u.mem_write(S,struct.pack('<I',3));u.mem_write(S+20,struct.pack('<i',start));u.mem_write(S+16,b'\x01');u.mem_write(P,struct.pack('<ii',123,456))
        trace=[];add=(syms['audio_uart_font_stroker_border_add']&~1) if compiled else 0x5683f2
        close=(syms['audio_uart_font_stroker_border_close']&~1) if compiled else 0x56834a
        def hook(u,pc,size,_):
            if pc==close:
                trace.append(('close',u.reg_read(UC_ARM_REG_R0)-S,u.reg_read(UC_ARM_REG_R1)))
                u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
            if pc!=add:return
            trace.append(('add',u.reg_read(UC_ARM_REG_R0)-S,struct.unpack('<ii',u.mem_read(u.reg_read(UC_ARM_REG_R1),8)),u.reg_read(UC_ARM_REG_R2)))
            u.reg_write(UC_ARM_REG_R0,7 if fail else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,P)
        u.emu_start((syms['audio_uart_font_stroker_border_move'] if compiled else 0x568636)|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(S,0x20))
    for case in [(-1,False),(-1,True),(0,False),(0,True),(2,False),(2,True)]:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b);print('PASS border move',case)

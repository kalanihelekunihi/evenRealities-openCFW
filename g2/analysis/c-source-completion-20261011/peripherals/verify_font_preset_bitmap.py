"""Bounded actual-C/stock bitmap-preset comparison with controlled outline cbox."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SLOT=0x20010000;ORIGIN=0x20010200
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('__attribute__((naked,used)) void audio_uart_font_outline_cbox(void*a,void*b){__asm__ volatile("bx lr");}\n')
    elf=Path(td)/'preset.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_preset_bitmap',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_preset_bitmap.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f: segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,mode,box,origin):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(SLOT,b'\0'*0x100);u.mem_write(ORIGIN,struct.pack('<ii',*origin))
        child=(syms['audio_uart_font_outline_cbox']&~1) if candidate else 0x527ace
        def hook(u,pc,size,_):
            if pc!=child:return
            u.mem_write(u.reg_read(UC_ARM_REG_R1),struct.pack('<iiii',*box))
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,SLOT);u.reg_write(UC_ARM_REG_R1,mode);u.reg_write(UC_ARM_REG_R2,ORIGIN)
        u.emu_start((syms['audio_uart_font_preset_bitmap'] if candidate else 0x5250de)|1,0x600000,count=10000)
        return bytes(u.mem_read(SLOT,0xa0))
    cases=[(m,b,o) for m in (0,1,2,3,4,5) for b in ((-90,-50,160,210),(0,0,20,40),(64,64,128,128)) for o in ((0,0),(17,-9))]
    for case in cases:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,[(i,a[i],b[i]) for i in range(len(a)) if a[i]!=b[i]][:10])
    print('PASS preset bitmap',len(cases))

"""Compare compiled C round-cap with stock for controlled arc-emitter outcomes."""
from pathlib import Path
import subprocess, tempfile, struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SOURCE=ROOT/'components/audio/uart_thread_source_candidate'
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'emit.c'
    shim.write_text('__attribute__((naked,used)) void audio_uart_font_stroker_arc_emit(void){__asm__ volatile("bx lr");}')
    elf=Path(d)/'round.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_round_cap',
                    str(SOURCE/'display_font_freetype_stroker_round_cap.c'),
                    str(SOURCE/'display_font_freetype_stroker_border_close.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    S=0x20010000
    def run(compiled,side,a,b,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(S,b'\0'*0xa0)
        u.mem_write(S,struct.pack('<IIii',a,b,100,-200));u.mem_write(S+0x30,struct.pack('<I',333))
        u.mem_write(S+0x34+side*0x20+16,b'\x01')
        trace=[];addr=(symbols['audio_uart_font_stroker_arc_emit']&~1) if compiled else 0x56851e
        def hook(u,pc,size,_):
            if pc!=addr:return
            sp=u.reg_read(UC_ARM_REG_SP)
            trace.append((u.reg_read(UC_ARM_REG_R0)-S,
                          u.reg_read(UC_ARM_REG_R1)-S,
                          u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3),
                          struct.unpack('<I',u.mem_read(sp,4))[0]))
            u.reg_write(UC_ARM_REG_R0,7 if fail else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,side)
        u.emu_start((symbols['audio_uart_font_stroker_round_cap'] if compiled else 0x568870)|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(S,0x90))
    cases=[(side,a,b,fail) for side in (0,1) for a,b in ((0,0xb40000),(0x123000,0x223000),(0x900000,0x200000)) for fail in (False,True)]
    for case in cases:
        stock=run(False,*case);source=run(True,*case)
        assert stock==source,(case,stock,source)
        print('PASS round cap',case)

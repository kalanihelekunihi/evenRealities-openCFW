"""Stock/compiled-C border line insertion and duplicate/error branches."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'grow.c';shim.write_text('__attribute__((naked,used)) void audio_uart_font_stroker_border_grow(void){__asm__ volatile("bx lr");}')
    elf=Path(d)/'add.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_border_add',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_border_add.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    B=0x20010000;P=0x20010100;T=0x20010200;NEW=0x20010300
    def run(compiled,count,active,new,flag,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(B,struct.pack('<IIIIIII',count,8,P,T,0,0,0));u.mem_write(B+16,bytes([active]))
        u.mem_write(P,struct.pack('<iiii',10,20,30,40)+b'\xaa'*48);u.mem_write(T,b'\xbb'*8)
        u.mem_write(NEW,struct.pack('<ii',*new))
        trace=[];addr=(symbols['audio_uart_font_stroker_border_grow']&~1) if compiled else 0x5682de
        def hook(u,address,size,_):
            if address==addr:
                trace.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
                u.reg_write(UC_ARM_REG_R0,7 if fail else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,B);u.reg_write(UC_ARM_REG_R1,NEW);u.reg_write(UC_ARM_REG_R2,flag)
        u.emu_start((symbols['audio_uart_font_stroker_border_add'] if compiled else 0x5683f2)|1,0x600000,count=5000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(B,28)),bytes(u.mem_read(P,64)),bytes(u.mem_read(T,8))
    cases=[(0,0,(50,60),0,False),(1,0,(10,20),1,False),(1,0,(11,21),0,False),(1,0,(12,21),0,False),(1,0,(50,60),1,False),(2,1,(50,60),0,False),(2,0,(50,60),1,True)]
    for case in cases:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a,b)
        print('PASS add',case,a[0])

"""Stock/compiled-C reverse-border transfers with bounded growth contract."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'grow.c';shim.write_text('__attribute__((naked,used)) void audio_uart_font_stroker_border_grow(void){__asm__ volatile("bx lr");}')
    elf=Path(d)/'reverse.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_reverse',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_stroker_reverse.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    S=0x20010000;L=S+0x34;R=S+0x54;LP=0x20010100;LT=0x20010200;RP=0x20010300;RT=0x20010400
    def run(compiled,count,start,suppress,fail,tags):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(L,struct.pack('<IIIIIII',2,16,LP,LT,1,0,0))
        u.mem_write(R,struct.pack('<IIIIIII',count,16,RP,RT,1,start,0))
        u.mem_write(LP,b''.join(struct.pack('<ii',100+i,200+i) for i in range(16)))
        u.mem_write(RP,b''.join(struct.pack('<ii',300+i,400+i) for i in range(16)))
        u.mem_write(LT,b'\xaa'*16);u.mem_write(RT,bytes(tags)+b'\0'*(16-len(tags)))
        trace=[];grow_addr=(symbols['audio_uart_font_stroker_border_grow']&~1) if compiled else 0x5682de
        def hook(u,addr,size,_):
            if addr==grow_addr:
                trace.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
                u.reg_write(UC_ARM_REG_R0,7 if fail else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,suppress)
        u.emu_start((symbols['audio_uart_font_stroker_reverse'] if compiled else 0x569532)|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(L,28)),bytes(u.mem_read(R,28)),bytes(u.mem_read(LP,128)),bytes(u.mem_read(LT,16))
    cases=[(2,2,0,False,[4,8]),(2,1,0,False,[4,8]),(4,1,0,False,[4,1,0,8]),(4,1,1,False,[4,1,0,8]),(5,1,0,False,[4,8,1,0,8]),(5,1,1,False,[4,8,1,0,8]),(4,1,1,True,[4,1,0,8])]
    for case in cases:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a,b)
        print('PASS reverse',case[:4],a[0])

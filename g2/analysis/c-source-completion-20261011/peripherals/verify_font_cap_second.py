"""Bounded native/C FT_Stroker_Outside branch and error transitions."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CHILDREN=[('round',0x568870,'audio_uart_font_stroker_round_cap'),('cos',0x528f8c,'audio_uart_font_vector_cos'),('sin',0x528f9a,'audio_uart_font_vector_sin'),('scale',0x5246f8,'audio_uart_font_scale_metric'),('divide',0x524754,'audio_uart_font_divide_metric'),('muldiv',0x524606,'audio_uart_font_mul_div'),('polar',0x5290fa,'audio_uart_font_vector_from_polar'),('add',0x5683f2,'audio_uart_font_stroker_border_add')]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,used)) void '+s+'(void){__asm__ volatile("bx lr");}\n' for _,_,s in CHILDREN))
    src=ROOT/'components/audio/uart_thread_source_candidate';elf=Path(d)/'cap.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_cap_second',str(src/'display_font_freetype_stroker_cap_second.c'),str(src/'display_font_freetype_stroker_border_close.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    S=0x20010000
    def run(compiled,join,side,length,turn,ratio,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(S,b'\0'*0xa0)
        u.mem_write(S,struct.pack('<IIII',0,turn&0xffffffff,1000,2000));u.mem_write(S+0x2c,struct.pack('<II',0x20000,333));u.mem_write(S+42,bytes([join]))
        trace=[];adds=0;scales=0;byaddr={(syms[sym]&~1 if compiled else stock):op for op,stock,sym in CHILDREN}
        def hook(u,pc,size,_):
            nonlocal adds,scales
            op=byaddr.get(pc)
            if op is None:return
            a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2)
            if op=='polar':trace.append((op,b,c));u.mem_write(a,struct.pack('<ii',11,-22));ret=0
            elif op=='add':
                adds+=1;trace.append((op,a-S,struct.unpack('<ii',u.mem_read(b,8)),c));ret=7 if fail==adds else 0
            elif op=='round':trace.append((op,a-S,b));ret=7 if fail else 0
            elif op=='scale':scales+=1;trace.append((op,a,b));ret=ratio if scales==1 else 777
            elif op in ('cos','sin'):trace.append((op,a));ret=0x8000 if op=='cos' else 1000
            else:trace.append((op,a,b,c) if op=='muldiv' else (op,a,b));ret=55 if op=='muldiv' else 444
            u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,side);u.reg_write(UC_ARM_REG_R2,length)
        u.emu_start((syms['audio_uart_font_stroker_cap_second'] if compiled else 0x568abe)|1,0x600000,count=20000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(S,0x90))
    cases=[(0,0,0,0,0,0),(1,0,0,0,0,0),(1,1,100,0,0,1),(2,0,100,0x100000,70000,0),(2,0,0,0x100000,70000,2),(2,1,100,0x100000,20000,0),(2,1,0,0x100000,20000,0),(2,1,0,0x100000,20000,1),(2,1,0,0x100000,20000,2),(3,0,100,0x100000,20000,0),(3,0,0,0x100000,70000,0)]
    for case in cases:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b);print('PASS cap second',case)

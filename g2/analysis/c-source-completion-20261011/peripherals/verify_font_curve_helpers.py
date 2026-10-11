"""Native/C conic split, angle continuity and border append with controlled children."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CHILDREN=[('angle',0x528fbc,'audio_uart_font_vector_angle'),('diff',0x52910e,'audio_uart_font_stroker_angle_diff'),('grow',0x5682de,'audio_uart_font_stroker_border_grow')]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,used)) void '+s+'(void){__asm__ volatile("bx lr");}\n' for _,_,s in CHILDREN))
    elf=Path(d)/'curve.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_conic_split',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_curve_helpers.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    S=0x20010000;A=S+0x100;B=S+0x104;P=S+0x200;T=S+0x300;C=S+0x400;E=S+0x408
    def run(compiled,kind,values,fail=False):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(S,b'\0'*0x500)
        trace=[];byaddr={(syms[sym]&~1 if compiled else stock):op for op,stock,sym in CHILDREN}
        def hook(u,pc,size,_):
            op=byaddr.get(pc)
            if op is None:return
            a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1)
            trace.append((op,a-S if op=='grow' else a,b))
            ret=(a+b)&0xffffffff if op=='angle' else (a-b)&0xffffffff if op=='diff' else (7 if fail else 0)
            u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if kind=='split':
            u.mem_write(S,struct.pack('<iiiiii',*values));u.reg_write(UC_ARM_REG_R0,S)
            sym='audio_uart_font_conic_split';addr=0x567fce
        elif kind=='cubic':
            u.mem_write(S,struct.pack('<iiiiiiii',*values));u.reg_write(UC_ARM_REG_R0,S)
            sym='audio_uart_font_cubic_split';addr=0x5680ce
        elif kind=='angle':
            u.mem_write(S,struct.pack('<iiiiii',*values));u.mem_write(A,struct.pack('<ii',11,22));u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,A);u.reg_write(UC_ARM_REG_R2,B)
            sym='audio_uart_font_conic_angle_ok';addr=0x568020
        elif kind=='cangle':
            u.mem_write(S,struct.pack('<iiiiiiii',*values));u.mem_write(A,struct.pack('<iii',11,22,33));u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,A);u.reg_write(UC_ARM_REG_R2,B);u.reg_write(UC_ARM_REG_R3,A+8)
            sym='audio_uart_font_cubic_angle_ok';addr=0x568176
        else:
            u.mem_write(S,struct.pack('<I',2));u.mem_write(S+8,struct.pack('<II',P,T));u.mem_write(S+16,b'\x01')
            u.mem_write(C,struct.pack('<ii',values[0],values[1]));u.mem_write(E,struct.pack('<ii',values[2],values[3]))
            u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,C);u.reg_write(UC_ARM_REG_R2,E)
            sym='audio_uart_font_stroker_border_conic';addr=0x56847a
        u.emu_start((syms[sym] if compiled else addr)|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0) if kind not in ('split','cubic') else None,trace,bytes(u.mem_read(S,0x40 if kind in ('split','cubic') else 0x20)),bytes(u.mem_read(A,12)),bytes(u.mem_read(P,0x50)),bytes(u.mem_read(T,0x10))
    cases=[('split',(0,0,100,50,300,100),False),('split',(-3,-5,4,7,8,9),False),('cubic',(0,0,100,50,300,100,400,0),False),('cubic',(-3,-5,4,7,8,9,11,13),False),('angle',(0,0,100,50,300,100),False),('angle',(0,0,0,0,100,0),False),('angle',(0,0,100,0,100,0),False),('cangle',(0,0,100,50,300,100,400,0),False),('cangle',(0,0,0,0,0,0,100,0),False),('cangle',(0,0,100,0,100,0,100,0),False),('border',(11,22,33,44),False),('border',(11,22,33,44),True)]
    for case in cases:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b);print('PASS curve helper',case[0],case[1])

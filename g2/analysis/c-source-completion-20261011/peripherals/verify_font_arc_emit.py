"""Compiled-C/stock arc stepping, Bezier geometry and errors, controlled math."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CHILDREN=[('polar',0x5290fa,'audio_uart_font_vector_from_polar'),('cos',0x528f8c,'audio_uart_font_vector_cos'),('sin',0x528f9a,'audio_uart_font_vector_sin'),('muldiv',0x524606,'audio_uart_font_mul_div'),('cubic',0x5684c2,'audio_uart_font_stroker_border_cubic')]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,used)) void '+s+'(void){__asm__ volatile("bx lr");}\n' for _,_,s in CHILDREN))
    elf=Path(d)/'arc.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_arc_emit',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_arc_emit.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    CENTER=0x20010000;BORDER=CENTER+0x100
    def run(compiled,sweep,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(CENTER,struct.pack('<ii',1000,-2000));u.mem_write(0x200ff000,struct.pack('<i',sweep))
        trace=[];byaddr={(syms[sym]&~1 if compiled else stock):op for op,stock,sym in CHILDREN};calls=0
        def hook(u,pc,size,_):
            nonlocal calls
            op=byaddr.get(pc)
            if op is None:return
            a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2);z=u.reg_read(UC_ARM_REG_R3)
            if op=='polar':trace.append((op,b,c));u.mem_write(a,struct.pack('<II',(b+c)&0xffffffff,(b-c)&0xffffffff));ret=0
            elif op=='cos':trace.append((op,a));ret=222
            elif op=='sin':trace.append((op,a));ret=111
            elif op=='muldiv':trace.append((op,a,b,c));ret=44
            else:
                calls+=1;trace.append((op,a-BORDER,struct.unpack('<ii',u.mem_read(b,8)),struct.unpack('<ii',u.mem_read(c,8)),struct.unpack('<ii',u.mem_read(z,8))));ret=7 if fail==calls else 0
            u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,BORDER);u.reg_write(UC_ARM_REG_R1,CENTER);u.reg_write(UC_ARM_REG_R2,333);u.reg_write(UC_ARM_REG_R3,0x123000)
        u.emu_start((syms['audio_uart_font_stroker_arc_emit'] if compiled else 0x56851e)|1,0x600000,count=20000)
        return u.reg_read(UC_ARM_REG_R0),trace
    cases=[(0,0),(0x100000,0),(0x5a0000,0),(0x700000,0),(-0x100000,0),(-0x5a0000,0),(-0x700000,0),(0x700000,1),(0x700000,2),(-0x700000,1)]
    for case in cases:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b);print('PASS arc emit',case,len(a[1]))

"""Native/C bounded subpath-start and process-corner transitions."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CHILDREN=[('first',0x5689e6,'audio_uart_font_stroker_cap_first'),('second',0x568abe,'audio_uart_font_stroker_cap_second'),('polar',0x5290fa,'audio_uart_font_vector_from_polar'),('move',0x568636,'audio_uart_font_stroker_border_move')]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,used)) void '+s+'(void){__asm__ volatile("bx lr");}\n' for _,_,s in CHILDREN))
    elf=Path(d)/'child.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_subpath_start',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_stroker_line_children.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_stroker_border_close.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    S=0x20010000
    def run(compiled,kind,a,b,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(S,b'\0'*0x90)
        u.mem_write(S,struct.pack('<IIII',a,b,100,200));u.mem_write(S+0x30,struct.pack('<I',333));u.mem_write(S+20,b'\x01')
        trace=[];byaddr={(symbols[sym]&~1 if compiled else stock):op for op,stock,sym in CHILDREN}
        def hook(u,pc,size,_):
            op=byaddr.get(pc)
            if op is None:return
            r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1);r2=u.reg_read(UC_ARM_REG_R2)
            if op=='polar':trace.append((op,r1,r2));u.mem_write(r0,struct.pack('<ii',11,-22));result=0
            elif op=='move':trace.append((op,r0-S,struct.unpack('<ii',u.mem_read(r1,8))));result=7 if fail==op else 0
            else:trace.append((op,r0-S,r1,r2));result=7 if fail==op else 0
            u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,123 if kind=='start' else 0x123000)
        if kind=='corner':u.reg_write(UC_ARM_REG_R2,123)
        sym='audio_uart_font_stroker_subpath_start' if kind=='start' else 'audio_uart_font_stroker_process_corner'
        addr=0x568ce2 if kind=='start' else 0x568d2a
        u.emu_start((symbols[sym] if compiled else addr)|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(S,0x80))
    cases=[('start',0,0,None),('start',0,0x10000,None),('start',0,0x10000,'first'),('start',0,0x10000,'second'),('start',0x10000,0,None),('corner',0,0,None),('corner',0,0,'move')]
    for case in cases:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b);print('PASS line child',case)

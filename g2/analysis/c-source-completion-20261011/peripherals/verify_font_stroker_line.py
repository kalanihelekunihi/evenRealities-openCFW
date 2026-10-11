"""Stock/compiled-C FT_Stroker_LineTo transitions with controlled native children."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CHILDREN=[('length',0x529086,'audio_uart_font_vector_length'),('angle',0x528fbc,'audio_uart_font_vector_angle'),
          ('polar',0x5290fa,'audio_uart_font_vector_from_polar'),('corner',0x568d2a,'audio_uart_font_stroker_process_corner'),
          ('start',0x568ce2,'audio_uart_font_stroker_subpath_start'),('add',0x5683f2,'audio_uart_font_stroker_border_add')]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,noinline,used)) void '+s+'(void){__asm__ volatile("bx lr");}\n' for _,_,s in CHILDREN))
    elf=Path(d)/'line.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_line',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_stroker_line.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    S=0x20010000;T=S+0x200
    def run(compiled,start,dx,dy,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(S,b'\0'*0x300)
        u.mem_write(S+8,struct.pack('<ii',100,200));u.mem_write(S+0x30,struct.pack('<I',333))
        u.mem_write(S+20,bytes([start]));u.mem_write(T,struct.pack('<ii',100+dx,200+dy))
        trace=[];byaddr={(symbols[sym]&~1 if compiled else stock):op for op,stock,sym in CHILDREN}
        def hook(u,pc,size,_):
            op=byaddr.get(pc)
            if op is None:return
            r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1);r2=u.reg_read(UC_ARM_REG_R2)
            if op=='length':trace.append((op,struct.unpack('<ii',u.mem_read(r0,8))));result=123
            elif op=='angle':trace.append((op,r0,r1));result=0x123000
            elif op=='polar':trace.append((op,r1,r2));u.mem_write(r0,struct.pack('<ii',11,-22));result=0
            elif op=='add':trace.append((op,r0-S,struct.unpack('<ii',u.mem_read(r1,8)),r2));result=7 if fail==op else 0
            else:trace.append((op,r0-S,r1,r2) if op=='corner' else (op,r0-S,r1));result=7 if fail==op else 0
            u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,T)
        u.emu_start((symbols['audio_uart_font_stroker_line'] if compiled else 0x568d86)|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(S,0x80))
    cases=[(0,0,0,None),(0,50,-30,None),(1,50,-30,None),(0,50,-30,'start'),(1,50,-30,'corner'),(0,50,-30,'add'),(1,-50,30,None)]
    for case in cases:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a,b)
        print('PASS line',case,a[0])

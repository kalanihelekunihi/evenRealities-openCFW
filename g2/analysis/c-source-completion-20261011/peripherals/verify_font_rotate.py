"""Stock/compiled-C FT_Vector_Rotate child ordering and rounding."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
children=[('normalize',0x528e18,'audio_uart_font_vector_normalize'),('core',0x528e5a,'audio_uart_font_vector_rotate_core'),('shrink',0x528db8,'audio_uart_font_vector_shrink')]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,noinline,used)) void '+sym+'(void){__asm__ volatile("bx lr");}\n' for _,_,sym in children))
    elf=Path(d)/'rotate.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_vector_rotate',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_rotate.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    V=0x20010000
    def run(compiled,xy,angle,shift):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(V,struct.pack('<ii',*xy))
        trace=[];byaddr={(symbols[sym]&~1 if compiled else stock):op for op,stock,sym in children}
        def hook(u,addr,size,_):
            op=byaddr.get(addr)
            if op is None:return
            r0=u.reg_read(UC_ARM_REG_R0)
            if op=='normalize':trace.append((op,struct.unpack('<ii',u.mem_read(r0,8))));u.reg_write(UC_ARM_REG_R0,shift&0xffffffff)
            elif op=='core':
                x,y=struct.unpack('<ii',u.mem_read(r0,8));trace.append((op,x,y,u.reg_read(UC_ARM_REG_R1)))
                u.mem_write(r0,struct.pack('<ii',-y,x));u.reg_write(UC_ARM_REG_R0,0)
            else:
                trace.append((op,r0));u.reg_write(UC_ARM_REG_R0,(r0+3)&0xffffffff)
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,V);u.reg_write(UC_ARM_REG_R1,angle)
        u.emu_start((symbols['audio_uart_font_vector_rotate'] if compiled else 0x529006)|1,0x600000,count=5000)
        return bytes(u.mem_read(V,8)),trace
    cases=[((0,0),1,1),((12,-13),0,1),((12,-13),500,1),((-100,222),777,4),((100,-222),800,-2),((-1,-2),123,0)]
    for case in cases:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a,b)
        print('PASS rotate',case)

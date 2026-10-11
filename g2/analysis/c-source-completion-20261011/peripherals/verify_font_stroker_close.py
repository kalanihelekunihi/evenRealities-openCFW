"""Stock/compiled-C FT_Stroker_EndSubPath call and error ordering."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
children=[('arc',0x5688b8,'audio_uart_font_stroker_arc'),('reverse',0x569532,'audio_uart_font_stroker_reverse'),('border',0x56834a,'audio_uart_font_stroker_border_close'),('line',0x568d86,'audio_uart_font_stroker_line'),('angle',0x52910e,'audio_uart_font_stroker_angle_diff'),('cap1',0x5689e6,'audio_uart_font_stroker_cap_first'),('cap2',0x568abe,'audio_uart_font_stroker_cap_second')]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,noinline,used)) void '+sym+'(void){__asm__ volatile("bx lr");}\n' for _,_,sym in children))
    elf=Path(d)/'close.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_close',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_stroker_close.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    STROKER=0x20010000
    def run(compiled,open_,same,direction,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(STROKER,b'\0'*0x80)
        u.mem_write(STROKER,struct.pack('<I',123));u.mem_write(STROKER+8,struct.pack('<ii',10,20));u.mem_write(STROKER+24,struct.pack('<III',345,10 if same else 30,20 if same else 40));u.mem_write(STROKER+36,struct.pack('<I',789));u.mem_write(STROKER+21,bytes([open_]))
        trace=[];byaddr={(symbols[sym]&~1 if compiled else stock):op for op,stock,sym in children}
        def hook(u,addr,size,_):
            op=byaddr.get(addr)
            if op is None:return
            args=(u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2))
            trace.append((op,args[:3] if op in ('arc','cap1','cap2') else args[:2] if op in ('border','line','angle','reverse') else args[:1]))
            u.reg_write(UC_ARM_REG_R0,direction if op=='angle' else (7 if op==fail else 0))
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,STROKER)
        u.emu_start((symbols['audio_uart_font_stroker_close'] if compiled else 0x5695f8)|1,0x600000,count=5000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(STROKER,0x40))
    cases=[(0,0,0,None),(0,1,0,None),(0,1,100,None),(0,1,-100,None),(0,1,-100,'cap1'),(0,1,100,'cap2'),(0,0,0,'line'),(1,1,0,None),(1,1,0,'arc'),(1,1,0,'reverse')]
    for case in cases:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a,b)
        print('PASS',case,a[0],[x[0] for x in a[1]])

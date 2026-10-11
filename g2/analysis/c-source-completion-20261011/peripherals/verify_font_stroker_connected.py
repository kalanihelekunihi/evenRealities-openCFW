"""Connected C curve geometry versus stock, with only first-corner and capacity hooks.

This runs the actual C angle, CORDIC, split, border append, curve and fixed
arithmetic bodies together. Allocator capacity and first-corner setup stay
controlled so the fixture requires no product heap or initialized contour.
"""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate'
NAMES=['display_font_freetype_stroker_conic','display_font_freetype_stroker_cubic','display_font_freetype_curve_helpers','display_font_freetype_border_add','display_font_freetype_border_cubic','display_font_freetype_vector_measure','display_font_freetype_angle_core','display_font_freetype_rotate_scalars','display_font_freetype_trig','display_font_freetype_cordic','display_font_freetype_polar','display_font_freetype_rotate','display_font_math','display_font_freetype_stroker_border_close']
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,used)) void '+s+'(void){__asm__ volatile("bx lr");}\n' for s in ('audio_uart_font_stroker_process_corner','audio_uart_font_stroker_subpath_start','audio_uart_font_stroker_border_grow')))
    elf=Path(d)/'connected.elf'
    division=ROOT/'components/audio/uart_power_config_offline/division_support.c'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_conic',*[str(SRC/(n+'.c')) for n in NAMES],str(division),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    S=0x20010000;C=S+0x200;D=S+0x208;T=S+0x210;LP=S+0x400;LT=S+0x600;RP=S+0x700;RT=S+0x900
    HOOKS=[('first',0x568d2a,'audio_uart_font_stroker_process_corner'),('corner',0x568ce2,'audio_uart_font_stroker_subpath_start'),('grow',0x5682de,'audio_uart_font_stroker_border_grow')]
    def run(compiled,kind,shape,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(S,b'\0'*0xa00)
        u.mem_write(S+8,struct.pack('<ii',100,200));u.mem_write(S+20,b'\x01');u.mem_write(S+0x30,struct.pack('<I',333))
        for side,pts,tags in ((0,LP,LT),(1,RP,RT)):
            u.mem_write(S+0x34+side*0x20+8,struct.pack('<II',pts,tags))
        if kind=='conic':
            (cx,cy),(tx,ty)=shape;u.mem_write(C,struct.pack('<ii',cx,cy));u.mem_write(T,struct.pack('<ii',tx,ty))
            target='audio_uart_font_stroker_conic';addr=0x568e52
        else:
            (cx,cy),(dx,dy),(tx,ty)=shape;u.mem_write(C,struct.pack('<ii',cx,cy));u.mem_write(D,struct.pack('<ii',dx,dy));u.mem_write(T,struct.pack('<ii',tx,ty))
            target='audio_uart_font_stroker_cubic';addr=0x569160
        trace=[];grow_count=0;byaddr={(syms[sym]&~1 if compiled else stock):op for op,stock,sym in HOOKS}
        def hook(u,pc,size,_):
            nonlocal grow_count
            op=byaddr.get(pc)
            if op is None:return
            a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2)
            trace.append((op,a-S,b,c) if op=='first' else (op,a-S,b))
            if op=='grow':grow_count+=1
            ret=7 if fail==op or (isinstance(fail,int) and op=='grow' and grow_count==fail) else 0
            u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,C);u.reg_write(UC_ARM_REG_R2,T if kind=='conic' else D)
        if kind=='cubic':u.reg_write(UC_ARM_REG_R3,T)
        u.emu_start((syms[target] if compiled else addr)|1,0x600000,count=40000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(S,0x80)),bytes(u.mem_read(LP,0x100)),bytes(u.mem_read(LT,0x20)),bytes(u.mem_read(RP,0x100)),bytes(u.mem_read(RT,0x20))
    cases=[('conic',((150,250),(300,350)),None),('conic',((101,201),(102,202)),None),('conic',((150,250),(300,350)),'first'),('conic',((150,250),(300,350)),1),('cubic',((150,250),(200,300),(300,350)),None),('cubic',((101,201),(102,202),(103,203)),None),('cubic',((150,250),(200,300),(300,350)),'first'),('cubic',((150,250),(200,300),(300,350)),1)]
    for case in cases:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b);print('PASS connected stroke',case[0],case[2])

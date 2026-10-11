"""Bounded stock/compiled-C FT_Stroker_CubicTo call and state transitions."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CHILDREN=[('ok',0x568176,'audio_uart_font_cubic_angle_ok'),('split',0x5680ce,'audio_uart_font_cubic_split'),('first',0x568d2a,'audio_uart_font_stroker_process_corner'),('corner',0x568ce2,'audio_uart_font_stroker_subpath_start'),('cos',0x528f8c,'audio_uart_font_vector_cos'),('divide',0x524754,'audio_uart_font_divide_metric'),('polar',0x5290fa,'audio_uart_font_vector_from_polar'),('conic',0x5684c2,'audio_uart_font_stroker_border_cubic'),('angle',0x528fbc,'audio_uart_font_vector_angle'),('length',0x529086,'audio_uart_font_vector_length'),('sin',0x528f9a,'audio_uart_font_vector_sin'),('muldiv',0x524606,'audio_uart_font_mul_div'),('add',0x5683f2,'audio_uart_font_stroker_border_add')]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,used)) void '+s+'(void){__asm__ volatile("bx lr");}\n' for _,_,s in CHILDREN))
    src=ROOT/'components/audio/uart_thread_source_candidate';elf=Path(d)/'conic.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_cubic',str(src/'display_font_freetype_stroker_cubic.c'),str(src/'display_font_freetype_stroker_border_close.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    S=0x20010000;C=S+0x200;D=S+0x208;T=S+0x210
    def run(compiled,first,fail,coincident,wide=False,opposite=False):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(S,b'\0'*0x400)
        u.mem_write(S+8,struct.pack('<ii',100,200));u.mem_write(S+20,bytes([first]));u.mem_write(S+40,bytes([wide]));u.mem_write(S+0x30,struct.pack('<I',333))
        if wide:
            for side in (0,1):
                u.mem_write(S+0x34+side*0x20,struct.pack('<I',1))
                u.mem_write(S+0x34+side*0x20+8,struct.pack('<I',S+0x100+side*0x20))
                u.mem_write(S+0x100+side*0x20,struct.pack('<ii',90,190))
        u.mem_write(C,struct.pack('<ii',100 if coincident else 150,200 if coincident else 250))
        u.mem_write(D,struct.pack('<ii',100 if coincident else 200,200 if coincident else 300))
        u.mem_write(T,struct.pack('<ii',100 if coincident else 300,200 if coincident else 350))
        trace=[];calls=0;angles=0;byaddr={(syms[sym]&~1 if compiled else stock):op for op,stock,sym in CHILDREN}
        def hook(u,pc,size,_):
            nonlocal calls,angles
            op=byaddr.get(pc)
            if op is None:return
            a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);c=u.reg_read(UC_ARM_REG_R2)
            if op=='ok':
                trace.append((op,tuple(struct.unpack('<iiiiiiii',u.mem_read(a,32)))))
                z=u.reg_read(UC_ARM_REG_R3)
                u.mem_write(b,struct.pack('<i',0x100000));u.mem_write(c,struct.pack('<i',0x140000));u.mem_write(z,struct.pack('<i',0x180000));ret=1
            elif op=='split':trace.append((op,));ret=0
            elif op=='polar':trace.append((op,b,c));u.mem_write(a,struct.pack('<ii',11,-22));ret=0
            elif op=='conic':
                calls+=1;trace.append((op,a-S,struct.unpack('<ii',u.mem_read(b,8)),struct.unpack('<ii',u.mem_read(c,8)),struct.unpack('<ii',u.mem_read(u.reg_read(UC_ARM_REG_R3),8))))
                ret=7 if fail==calls else 0
            elif op=='angle':
                angles+=1;trace.append((op,a,b));ret=(0x800000 if angles in (2,5) else 0x100000) if opposite else 0x100000
            elif op=='length':trace.append((op,struct.unpack('<ii',u.mem_read(a,8))));ret=123
            elif op=='add':trace.append((op,a-S,struct.unpack('<ii',u.mem_read(b,8)),c));ret=7 if fail=='add' else 0
            else:
                trace.append((op,a-S,b,c) if op=='first' else ((op,a-S,b) if op=='corner' else ((op,a) if op in ('cos','sin','length') else (op,a,b))))
                ret={'first':7 if fail=='first' else 0,'corner':7 if fail=='corner' else 0,'cos':0x10000,'divide':444,'sin':0x1000,'muldiv':55}[op]
            u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,C);u.reg_write(UC_ARM_REG_R2,D);u.reg_write(UC_ARM_REG_R3,T)
        u.emu_start((syms['audio_uart_font_stroker_cubic'] if compiled else 0x569160)|1,0x600000,count=20000)
        return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(S,0x80))
    cases=[(1,None,True),(1,None,False),(0,None,False),(1,'first',False),(0,'corner',False),(1,1,False),(1,2,False),(1,None,False,True,False),(1,None,False,True,True)]
    for case in cases:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b);print('PASS cubic',case)

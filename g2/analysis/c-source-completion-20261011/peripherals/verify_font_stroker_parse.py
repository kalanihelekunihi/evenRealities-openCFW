"""Stock/compiled-C FT_Stroker_ParseOutline callback traces and exits."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
children=[('reset',0x56882a,'audio_uart_font_stroker_reset',0),('begin',0x5694e0,'audio_uart_font_stroker_begin',1),('line',0x568d86,'audio_uart_font_stroker_line',1),('conic',0x568e52,'audio_uart_font_stroker_conic',2),('cubic',0x569160,'audio_uart_font_stroker_cubic',3),('close',0x5695f8,'audio_uart_font_stroker_close',0)]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'children.c';shim.write_text(''.join('__attribute__((naked,noinline,used)) void '+name+'(void){__asm__ volatile("bx lr");}\n' for _,_,name,_ in children))
    elf=Path(d)/'parse.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_parse_outline',
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_stroker_parse.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    OUTLINE=0x20010000;POINTS=0x20010100;TAGS=0x20010200;ENDS=0x20010300;STROKER=0x20010400
    def run(compiled,pts,tags,opened=0,fail=None):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(OUTLINE,struct.pack('<hhIIII',1,len(pts),POINTS,TAGS,ENDS,0))
        u.mem_write(POINTS,b''.join(struct.pack('<ii',*p) for p in pts))
        u.mem_write(TAGS,bytes(tags));u.mem_write(ENDS,struct.pack('<h',len(pts)-1))
        trace=[];byaddr={(symbols[sym]&~1 if compiled else stock): (op,n) for op,stock,sym,n in children}
        def hook(u,addr,size,_):
            item=byaddr.get(addr)
            if item is None:return
            op,n=item;regs=[UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
            args=tuple(struct.unpack('<ii',u.mem_read(u.reg_read(reg),8)) for reg in regs[:n])
            trace.append((op,args))
            if op=='begin':u.mem_write(STROKER+20,bytes([opened&0xff]))
            u.reg_write(UC_ARM_REG_R0,7 if fail==op else 0)
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,STROKER);u.reg_write(UC_ARM_REG_R1,OUTLINE);u.reg_write(UC_ARM_REG_R2,opened)
        addr=symbols['audio_uart_font_stroker_parse_outline'] if compiled else 0x569748
        u.emu_start(addr|1,0x600000,count=30000)
        return u.reg_read(UC_ARM_REG_R0),trace
    cases=[('line',[(0,0),(100,0),(100,100),(0,100)],[1,1,1,1],0,None),
       ('conic',[(0,0),(50,100),(100,0)],[1,0,1],0,None),
       ('conic-chain',[(0,0),(30,60),(60,70),(100,0)],[1,0,0,1],0,None),
       ('cubic',[(0,0),(20,80),(80,80),(100,0)],[1,2,2,1],0,None),
       ('first-conic',[(20,80),(80,80),(100,0)],[0,0,1],0,None),
       ('open',[(0,0),(100,0)],[1,1],1,None),
       ('bad-cubic',[(0,0),(20,80),(100,0)],[1,2,1],0,None),
       ('line-error',[(0,0),(100,0)],[1,1],0,'line'),
       ('begin-error',[(0,0),(100,0)],[1,1],0,'begin')]
    for name,pts,tags,opened,fail in cases:
        a=run(False,pts,tags,opened,fail);b=run(True,pts,tags,opened,fail)
        assert a==b,(name,a,b)
        print('PASS',name,a)

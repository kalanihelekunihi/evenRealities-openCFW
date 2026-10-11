"""Stock/compiled-C border growth with controlled allocator failures."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    shim=Path(d)/'zero.c';shim.write_text('void audio_uart_buffer_zero(void *p,unsigned n,unsigned v){volatile unsigned char *b=p;for(unsigned i=0;i<n;i++)b[i]=(unsigned char)v;}')
    elf=Path(d)/'grow.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_border_grow',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_border_grow.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_realloc.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_glyph_leaf.c'),str(shim),'-Wl,--unresolved-symbols=ignore-all','-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    BORDER=0x20010000;MEMORY=0x20010100;OLD_P=0x20020000;OLD_T=0x20021000;NEW_P=0x20030000;NEW_T=0x20031000
    def run(compiled,count,capacity,additional,fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_map(0x300000,0x1000);u.mem_write(0x300000,b'\x70\x47'*128)
        u.mem_write(MEMORY,struct.pack('<IIII',0,0x300001,0x300011,0x300021))
        u.mem_write(BORDER,struct.pack('<IIIIIII',count,capacity,OLD_P if capacity else 0,OLD_T if capacity else 0,0,0,MEMORY))
        u.mem_write(OLD_P,b'\x55'*128);u.mem_write(OLD_T,b'\x66'*32)
        u.mem_write(NEW_P,b'\xaa'*128);u.mem_write(NEW_T,b'\xbb'*32)
        trace=[];alloc_count=[0]
        def hook(u,addr,size,_):
            if addr not in (0x300000,0x300010,0x300020):return
            if addr==0x300000:
                amount=u.reg_read(UC_ARM_REG_R1);old=0;kind='alloc';
            elif addr==0x300020:
                old=u.reg_read(UC_ARM_REG_R3);amount=u.reg_read(UC_ARM_REG_R2);kind='realloc'
            else:
                old=u.reg_read(UC_ARM_REG_R1);amount=0;kind='free'
            trace.append((kind,old,amount))
            if kind=='free':result=0
            else:
                alloc_count[0]+=1
                result=0 if fail==alloc_count[0] else (NEW_P if alloc_count[0]==1 else NEW_T)
                if result and kind=='realloc':u.mem_write(result,bytes(u.mem_read(old,min(amount,capacity*(8 if alloc_count[0]==1 else 1)))))
            u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,BORDER);u.reg_write(UC_ARM_REG_R1,additional)
        u.emu_start((symbols['audio_uart_font_stroker_border_grow'] if compiled else 0x5682de)|1,0x600000,count=30000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(BORDER,28)),bytes(u.mem_read(NEW_P,128)),bytes(u.mem_read(NEW_T,32)),trace
    cases=[(1,8,1,None),(0,0,1,None),(2,2,5,None),(2,2,5,1),(2,2,5,2)]
    for case in cases:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a,b)
        print('PASS grow',case,a[0],a[-1])

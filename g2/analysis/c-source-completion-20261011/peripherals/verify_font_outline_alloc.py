"""Stock/compiled-C FT_Outline_New and Done with controlled allocator callbacks."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'storage.elf'
    shim=Path(d)/'zero.c'
    shim.write_text('void audio_uart_buffer_zero(void *p,unsigned n,unsigned value){volatile unsigned char *b=p;for(unsigned i=0;i<n;i++)b[i]=(unsigned char)value;}')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_outline_new',
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_outline_storage.c'),
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_glyph_leaf.c'),
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_get_glyph.c'),
      str(ROOT/'components/audio/uart_thread_source_candidate/byte_copy.c'),str(shim),
      '-Wl,--gc-sections','-Wl,-u,audio_uart_font_outline_done','-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    LIBRARY=0x20010000;MEMORY=0x20010100;OUTLINE=0x20010200;POOL=0x20020000
    def run(compiled,kind,points,contours):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_map(0x300000,0x1000)
        u.mem_write(0x300000,b'\x70\x47'*128)
        u.mem_write(LIBRARY,struct.pack('<I',MEMORY))
        u.mem_write(MEMORY,struct.pack('<III',0,0x300001,0x300011))
        u.mem_write(OUTLINE,b'\xaa'*20)
        if kind=='done':
            u.mem_write(OUTLINE,struct.pack('<hhIIII',1,3,POOL,POOL+32,POOL+64,points))
        allocations=[];frees=[];offset=[0]
        def callback(u,addr,size,_):
            if addr==0x300000:
                amount=u.reg_read(UC_ARM_REG_R1);allocated=POOL+offset[0];offset[0]+=max(4,(amount+3)&~3)
                allocations.append((amount,allocated));u.reg_write(UC_ARM_REG_R0,allocated)
            elif addr==0x300010:
                frees.append(u.reg_read(UC_ARM_REG_R1))
            else:return
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,callback)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,LIBRARY)
        if kind=='done':
            u.reg_write(UC_ARM_REG_R1,OUTLINE)
            addr=symbols['audio_uart_font_outline_done'] if compiled else 0x527abc
        else:
            u.reg_write(UC_ARM_REG_R1,points&0xffffffff)
            u.reg_write(UC_ARM_REG_R2,contours&0xffffffff);u.reg_write(UC_ARM_REG_R3,OUTLINE)
            addr=symbols['audio_uart_font_outline_new'] if compiled else 0x52797a
        u.emu_start(addr|1,0x600000,count=30000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(OUTLINE,20)),allocations,frees
    cases=[(0,0),(1,1),(3,1),(-1,1),(1,-1),(1,2),(32768,1)]
    for points,contours in cases:
        a=run(False,'new',points,contours);b=run(True,'new',points,contours)
        assert a==b,(points,contours,a,b)
        print('PASS',points,contours,a[0],len(a[2]))

    for flags in [0,1,3]:
        a=run(False,'done',flags,0);b=run(True,'done',flags,0)
        assert a==b,('done',flags,a,b)
        print('PASS done',flags,len(a[3]))

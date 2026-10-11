"""Actual C/native nanopb buffer callback cursor and copy comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_queue_copy_bytes(void *p,const void *s,uint32_t n){volatile uint8_t *d=p;const volatile uint8_t *a=s;for(uint32_t i=0;i<n;i++)d[i]=a[i];return p;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_buffer_write',str(ROOT/'components/audio/uart_thread_source_candidate/display_pb_ostream_buffer.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,count):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(0x20081000,struct.pack('<IIIII',0,0x20082000,100,0,0))
        u.mem_write(0x20082000,b'\xaa'*32);u.mem_write(0x20083000,bytes(range(32)))
        u.reg_write(UC_ARM_REG_R0,0x20081000);u.reg_write(UC_ARM_REG_R1,0x20083000);u.reg_write(UC_ARM_REG_R2,count)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                if address!=0x439be4:return
                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
                uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['audio_pb_buffer_write'] if candidate else 0x4905e0)|1,0x600000,count=500)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20081000,20)),bytes(u.mem_read(0x20082000,32))
    for count in [0,1,8,17,32]:
        native=run(False,count);compiled=run(True,count)
        assert native==compiled,(count,native,compiled)
        print('PASS nanopb buffer',count)

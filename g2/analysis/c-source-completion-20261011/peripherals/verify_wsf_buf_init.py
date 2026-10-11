"""Bounded actual compiled-C/native WsfBufInit state comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c'
    shim.write_text('''#include <stdint.h>
void *audio_wsf_pool_list; volatile uint8_t audio_wsf_pool_count;
volatile uint16_t audio_wsf_pool_used_bytes;
''')
    elf=Path(td)/'a.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_wsf_buffer_init',str(ROOT/'components/audio/uart_thread_source_candidate/display_wsf_buf_init.c'),str(shim),'-o',str(elf)],check=True)
    syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,bytes_,configs):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000)
        mem=0x20080000;cfg=0x20090000
        u.mem_write(mem,b'\xcc'*1024)
        for i,(size,count) in enumerate(configs):u.mem_write(cfg+4*i,struct.pack('<HBB',size,count,0))
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        if c:plist,pcount,pused=(syms[k] for k in ('audio_wsf_pool_list','audio_wsf_pool_count','audio_wsf_pool_used_bytes'))
        else:plist,pcount,pused=0x20074eec,0x20075044,0x20074f4a
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        for reg,val in ((UC_ARM_REG_R0,bytes_),(UC_ARM_REG_R1,mem),(UC_ARM_REG_R2,len(configs)),(UC_ARM_REG_R3,cfg)):u.reg_write(reg,val)
        u.emu_start((syms['audio_wsf_buffer_init'] if c else 0x530364)|1,0x600000,count=10000)
        norm=lambda p:p-mem if mem<=p<mem+1024 else p
        desc=[]
        for i in range(len(configs)):
            a=mem+12*i;desc.append((struct.unpack('<H',u.mem_read(a,2))[0],u.mem_read(a+2,1)[0],norm(rd(a+4)),norm(rd(a+8))))
        return (u.reg_read(UC_ARM_REG_R0),norm(rd(plist)),u.mem_read(pcount,1)[0],struct.unpack('<H',u.mem_read(pused,2))[0],tuple(desc),bytes(u.mem_read(mem+12*len(configs),max(0,min(160,bytes_-12*len(configs))))))
    for bytes_,configs in [(64,[]),(128,[(8,2)]),(160,[(9,1),(16,2)]),(16,[(8,2)]),(32,[(8,4)])]:
        native,source=run(False,bytes_,configs),run(True,bytes_,configs)
        assert native==source,(bytes_,configs,native,source)
        print('PASS WSF init',bytes_,configs)

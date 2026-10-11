"""Bounded compiled-C/native WSF timer removal on head/middle/miss."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_wsf_timer_list[2];
void audio_wsf_cs_enter(void){} void audio_wsf_cs_exit(void){}
''')
    elf=Path(td)/'a.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_wsf_timer_remove',str(ROOT/'components/audio/uart_thread_source_candidate/display_wsf_timer_remove.c'),str(shim),'-o',str(elf)],check=True)
    syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for target in (0,1,2):
        obs=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            u.mem_map(0x20000000,0x100000)
            queue=syms['audio_wsf_timer_list'] if compiled else 0x200741b0
            nodes=[0x20080000,0x20080020]
            wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
            wr(queue,nodes[0]);wr(queue+4,nodes[1]);wr(nodes[0],nodes[1]);wr(nodes[1],0)
            u.mem_write(nodes[0]+0xd,b'\x01');u.mem_write(nodes[1]+0xd,b'\x01')
            calls=[]
            cuts={syms['audio_wsf_cs_enter']&~1:'enter',syms['audio_wsf_cs_exit']&~1:'exit'} if compiled else {0x52b8a4:'enter',0x52b8b6:'exit'}
            def hook(uc,a,size,_):
                if a in cuts:calls.append(cuts[a]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(UC_ARM_REG_R0,nodes[target] if target<2 else 0x20080040)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.emu_start((syms['audio_wsf_timer_remove'] if compiled else 0x52a3fc)|1,0x600000,count=10000)
            rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
            obs.append((rd(queue),rd(queue+4),rd(nodes[0]),rd(nodes[1]),u.mem_read(nodes[0]+0xd,1),u.mem_read(nodes[1]+0xd,1),calls))
        assert obs[0]==obs[1],(target,obs)
        print('PASS timer remove',target)

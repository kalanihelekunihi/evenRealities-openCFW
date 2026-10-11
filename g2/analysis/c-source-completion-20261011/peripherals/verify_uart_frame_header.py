"""Bounded original-byte versus compiled C TinyFrame header comparison."""
from pathlib import Path
import struct
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP)
from unicorn.unicorn_const import UC_HOOK_CODE

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SOURCE=ROOT/'components/audio/uart_thread_source_candidate/frame_response.c'
HARNESS=r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
extern uint32_t audio_uart_frame_header(void*,void*,const void*);
int main(int argc,char**argv) {
    if(argc!=4) return 2;
    uint8_t tf[0x7160]={0},out[16]={0},desc[24]={0};
    uint16_t seq=(uint16_t)strtoul(argv[1],0,0);
    uint16_t id=(uint16_t)strtoul(argv[2],0,0);
    uint16_t type=(uint16_t)strtoul(argv[3],0,0);
    *(uint16_t*)(void*)(tf+0xe)=seq;
    tf[0xc]=(uint8_t)(seq&1);
    *(uint16_t*)(void*)desc=id;
    desc[2]=(uint8_t)(id!=0);
    *(uint16_t*)(void*)(desc+4)=type;
    *(uint16_t*)(void*)(desc+12)=0x1234;
    uint32_t n=audio_uart_frame_header(tf,out,desc);
    printf("%u %u %u ",n,*(uint16_t*)(void*)desc,*(uint16_t*)(void*)(tf+0xe));
    for(uint32_t i=0;i<n;++i) printf("%02x",out[i]);
    puts("");
}
'''

def stock(seq,id_value,type_value):
    uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,BLOB)
    uc.mem_map(0x20000000,0x100000)
    tf,out,desc,ret=0x20001000,0x20009000,0x2000a000,0x600000
    uc.mem_write(tf+0xe,struct.pack('<H',seq));uc.mem_write(tf+0xc,bytes([seq&1]))
    uc.mem_write(desc,struct.pack('<H',id_value))
    uc.mem_write(desc+2,bytes([int(id_value!=0)]))
    uc.mem_write(desc+4,struct.pack('<H',type_value))
    uc.mem_write(desc+12,struct.pack('<H',0x1234))
    uc.reg_write(UC_ARM_REG_SP,0x200ff000)
    uc.reg_write(UC_ARM_REG_LR,ret|1)
    uc.reg_write(UC_ARM_REG_R0,tf);uc.reg_write(UC_ARM_REG_R1,out)
    uc.reg_write(UC_ARM_REG_R2,desc)
    uc.hook_add(UC_HOOK_CODE,lambda m,a,s,u:m.emu_stop() if a==ret else None)
    uc.emu_start(0x491f55,ret,count=10000)
    n=uc.reg_read(UC_ARM_REG_R0)
    return (n,struct.unpack('<H',uc.mem_read(desc,2))[0],
            struct.unpack('<H',uc.mem_read(tf+0xe,2))[0],
            bytes(uc.mem_read(out,n)).hex())

with tempfile.TemporaryDirectory() as tmp:
    temp=Path(tmp);(temp/'harness.c').write_text(HARNESS)
    build=subprocess.run(['cc','-O2','-ffunction-sections','-fdata-sections',
                          str(temp/'harness.c'),str(SOURCE),'-Wl,-dead_strip',
                          '-o',str(temp/'header')],capture_output=True,text=True)
    if build.returncode: raise RuntimeError(build.stderr)
    cases=[(0,0,0),(1,0,0x1234),(0x7fff,0,0xffff),
           (0x8000,0xabcd,0x0009),(0x1234,0x8001,0x000c)]
    for case in cases:
        result=subprocess.check_output([str(temp/'header'),*map(str,case)],text=True).split()
        compiled=(int(result[0]),int(result[1]),int(result[2]),result[3])
        original=stock(*case)
        assert compiled==original,(case,compiled,original)
    print(f'PASS {len(cases)}/{len(cases)} stock bytes versus compiled C header cases')

#!/usr/bin/env python3
"""Compare stock/C LittleFS directory drop with controlled descendants."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_file_lfs_dir_drop_4cc5a2.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-file-lfs-dir-drop-4cc5a2';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
    p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
    shim.write_text('''#include <stdint.h>
struct attr {uint32_t tag;const void *buffer;};
int32_t g2_lfs_dir_getgstate(void*a,void*b,void*c){(void)a;(void)b;(void)c;return 0;}
int32_t g2_lfs_dir_commit(void*a,void*b,const struct attr*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
''')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_file_lfs_dir_drop_4cc5a2',str(SOURCE),str(shim),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(compiled,split,get_ret,commit_ret):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000)
        fs=0x20070000;directory=0x20071000;tail=0x20072000
        u.mem_write(tail+23,bytes((split,)))
        u.mem_write(tail+24,(0x1234).to_bytes(4,'little')+(0x5678).to_bytes(4,'little'))
        calls=[]
        hooks={(syms['g2_lfs_dir_getgstate']&~1 if compiled else 0x4cbefc):'get',
               (syms['g2_lfs_dir_commit']&~1 if compiled else 0x4cd388):'commit'}
        def hook(cpu,pc,size,data):
            k=hooks.get(pc)
            if not k:return
            r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
            if k=='get':calls.append(('get',r0==fs,r1==tail,r2==fs+0x48));result=get_ret
            else:
                tag=int.from_bytes(cpu.mem_read(r2,4),'little')
                pointer=int.from_bytes(cpu.mem_read(r2+4,4),'little')
                pair=tuple(int.from_bytes(cpu.mem_read(pointer+i*4,4),'little') for i in range(2))
                calls.append(('commit',r0==fs,r1==directory,tag,pointer==tail+24,pair,r3))
                result=commit_ret
            cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(A.UC_ARM_REG_R0,fs);u.reg_write(A.UC_ARM_REG_R1,directory);u.reg_write(A.UC_ARM_REG_R2,tail)
        u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        entry=syms['audio_file_lfs_dir_drop_4cc5a2'] if compiled else 0x4cc5a2
        u.emu_start(entry|1,0x600000,count=10000)
        result=u.reg_read(A.UC_ARM_REG_R0)
        if result&0x80000000:result-=0x100000000
        return result,bytes(u.mem_read(tail+23,9)).hex(),calls
    cases=[]
    for split in (0,1):
        for get_ret in (-5,0):
            for commit_ret in (-5,0):
                n=run(False,split,get_ret,commit_ret);c=run(True,split,get_ret,commit_ret)
                if n!=c:raise AssertionError((split,get_ret,commit_ret,n,c))
                cases.append((split,get_ret,commit_ret))
    row={'status':'PASS_BOUNDED_MAIN_FILE_LFS_DIR_DROP_NATIVE_C','source':str(SOURCE.relative_to(ROOT)),
         'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,
         'native_c_cases':len(cases),'scope':'Directory gstate, tail tag and pair, and commit outcomes at controlled descendant boundaries.'}
    path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())

#!/usr/bin/env python3
"""Compare bounded stock/C LittleFS removal error and file-commit paths."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_file_lfs_remove_core_4ce4dc.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-file-lfs-remove-core-4ce4dc';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
    p=Path(td);shim=p/'shim.c';elf=p/'test.elf'
    shim.write_text('''#include <stdint.h>
struct attr {uint32_t tag;const void *buffer;};
int32_t audio_file_lfs_forceconsistency(void*a){(void)a;return 0;}
int32_t audio_file_lfs_dir_find(void*a,void*b,const char**c,uint16_t*d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_file_lfs_dir_get(void*a,void*b,uint32_t c,uint32_t d,void*e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
void audio_file_lfs_ctz_fromle32(void*a){(void)a;}
int32_t g2_lfs_dir_fetch(void*a,void*b,const uint32_t*c){(void)a;(void)b;(void)c;return 0;}
int32_t g2_lfs_fs_preporphans(void*a,int8_t b){(void)a;(void)b;return 0;}
int32_t g2_lfs_dir_commit(void*a,void*b,const struct attr*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t g2_lfs_fs_pred(void*a,const uint32_t*b,void*c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_file_lfs_dir_drop_4cc5a2(void*a,void*b,void*c){(void)a;(void)b;(void)c;return 0;}
''')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_file_lfs_remove_core_4ce4dc',str(SOURCE),str(shim),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    native={'force':0x4cf9e0,'find':0x4cc04a,'get':0x4cb3c8,'fetch':0x4cbedc,
            'prep':0x4cf570,'commit':0x4cd388,'pred':0x4cf40a,'drop':0x4cc5a2}
    source={'force':'audio_file_lfs_forceconsistency','find':'audio_file_lfs_dir_find',
            'get':'audio_file_lfs_dir_get','fetch':'g2_lfs_dir_fetch',
            'prep':'g2_lfs_fs_preporphans','commit':'g2_lfs_dir_commit',
            'pred':'g2_lfs_fs_pred','drop':'audio_file_lfs_dir_drop_4cc5a2'}
    def run(compiled,force_ret,tag,commit_ret,stop='',count=0,split=0):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000)
        fs=0x20070000;path=0x20071000;u.mem_write(path,b'/tp_42.bin\0')
        u.mem_write(fs+0x28,(0x20072000).to_bytes(4,'little'))
        hooks={(syms[source[k]]&~1 if compiled else addr):k for k,addr in native.items()};calls=[]
        def hook(cpu,pc,size,data):
            k=hooks.get(pc)
            if not k:return
            r0,r1,r2,r3=(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
            if k=='force':calls.append(('force',r0==fs));value=force_ret
            elif k=='find':calls.append(('find',r0==fs,int.from_bytes(cpu.mem_read(r2,4),'little')==path,r3==0));value=tag
            elif k=='get':
                calls.append(('get',r0==fs,r2, r3))
                out=int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),'little')
                cpu.mem_write(out,(0x1234).to_bytes(4,'little')+(0x5678).to_bytes(4,'little'))
                value=-5 if stop=='get' else 0x20000408
            elif k=='fetch':
                pair=tuple(int.from_bytes(cpu.mem_read(r2+i*4,4),'little') for i in range(2))
                calls.append(('fetch',r0==fs,pair))
                cpu.mem_write(r1+20,count.to_bytes(2,'little')+bytes((0,split)))
                cpu.mem_write(r1,(0x1234).to_bytes(4,'little')+(0x5678).to_bytes(4,'little'))
                value=-5 if stop=='fetch' else 0
            elif k=='prep':calls.append(('prep',r0==fs,r1 if r1<128 else r1-256));value=-5 if stop==('prep_plus' if r1==1 else 'prep_minus') else 0
            elif k=='commit':
                atag=int.from_bytes(cpu.mem_read(r2,4),'little')
                calls.append(('commit',r0==fs,atag,r3));value=commit_ret
            elif k=='pred':calls.append(('pred',r0==fs));value=-5 if stop=='pred' else 0
            else:calls.append(('drop',r0==fs));value=-5 if stop=='drop' else 0
            cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(A.UC_ARM_REG_R0,fs);u.reg_write(A.UC_ARM_REG_R1,path);u.reg_write(A.UC_ARM_REG_R2,0)
        u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        entry=syms['audio_file_lfs_remove_core_4ce4dc'] if compiled else 0x4ce4dc
        u.emu_start(entry|1,0x600000,count=20000)
        result=u.reg_read(A.UC_ARM_REG_R0)
        if result&0x80000000:result-=0x100000000
        head=int.from_bytes(u.mem_read(fs+0x28,4),'little')
        return result,head,calls
    cases=[]
    for force in (-5,0):
        for tag in (-2,0x001ffc00,0x00100400,0x00100800):
            for commit in (-5,0):
                n=run(False,force,tag,commit);c=run(True,force,tag,commit)
                if n!=c:raise AssertionError((force,tag,commit,n,c))
                cases.append((force,tag,commit))
    directory_tag=0x00200400
    for stop in ('get','fetch','prep_plus','commit','prep_minus','pred','drop',''):
        for count,split in ((0,0),(1,0),(0,1)):
            commit=-5 if stop=='commit' else 0
            n=run(False,0,directory_tag,commit,stop,count,split)
            c=run(True,0,directory_tag,commit,stop,count,split)
            if n!=c:raise AssertionError((stop,count,split,n,c))
            cases.append((stop,count,split))
    row={'status':'PASS_BOUNDED_MAIN_FILE_LFS_REMOVE_CORE_NATIVE_C',
         'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'payload_sha256':PINNED,'native_c_cases':len(cases),
         'scope':'Force-consistency, path lookup, invalid id, file commit, and directory get/fetch/nonempty/orphan/commit/pred/drop branches at controlled call boundaries.'}
    path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())

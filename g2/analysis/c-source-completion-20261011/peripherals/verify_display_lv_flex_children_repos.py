"""Bounded compiled ARM C/native flex repositioning with named child cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_flex_children_repos.c'
with tempfile.TemporaryDirectory() as td:
    obj=Path(td)/'repos.o';shim=Path(td)/'shim.c';elf=Path(td)/'repos.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(SRC),'-o',str(obj)],check=True)
    imports=[x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
    shim.write_text('#include <stdint.h>\n'+''.join('uint32_t '+n+
        '(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\n' for n in imports))
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_children_repos_48c14e',
                    str(obj),str(shim),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    cases=[('empty',1,0,0,0),('row_two',1,2,0,0),('row_hidden',1,2,1,0),
           ('row_reverse',5,2,0,0),('row_rtl',1,2,0,1),('column_two',0,2,0,0),
           ('row_grow',1,1,0,0),('row_grow_resize',1,1,0,0),('row_cross_end',1,1,0,0),
           ('row_cross_center',1,1,0,0),('column_cross_end',0,1,0,0)]
    for name,flags,count,hidden,rtl in cases:
        out=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            object,flex,track,child0,child1=0x20003000,0x20003100,0x20003200,0x20003400,0x20003500
            first=count-1 if flags&4 else 0;end=-1 if flags&4 else count
            cross_place=1 if name.endswith('cross_end') else 2 if name=='row_cross_center' else 0
            u.mem_write(flex,struct.pack('<BBBB',0,cross_place,0,flags))
            if name.startswith('row_grow'):
                u.mem_write(track,struct.pack('<iiiIIII',10,6 if name=='row_grow_resize' else 4,0,count,0x20003800,1,0))
                u.mem_write(0x20003800,struct.pack('<IiiIII',child0,4,100,0,1,0))
            else:u.mem_write(track,struct.pack('<iiiIIII',10,10,10,count,0,0,0))
            for a,x in ((child0,10),(child1,14)):
                u.mem_write(a+0x14,struct.pack('<iiii',x,20,x+3,22))
            sp=0x200ff000
            u.mem_write(sp,struct.pack('<iiiii',10,20,20,0,track))
            u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
            for r,v in ((UC_ARM_REG_R0,object),(UC_ARM_REG_R1,flex),(UC_ARM_REG_R2,first),(UC_ARM_REG_R3,end)):u.reg_write(r,v)
            mapping={(syms[n]&~1 if is_c else (0x440656 if n=='audio_uart_display_size_changed' else int(n.rsplit('_',1)[1],16))):n for n in imports if n!='audio_uart_lv_flex_repos_alloc_failure'}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
                short='440656' if n=='audio_uart_display_size_changed' else n.rsplit('_',1)[1];ret=0
                if short=='44dce2':ret=(child0,child1)[r1] if 0<=r1<count else 0
                elif short=='48c770':
                    p=uc.reg_read(UC_ARM_REG_R2);idx=struct.unpack('<i',uc.mem_read(p,4))[0]+(-1 if r1 else 1)
                    uc.mem_write(p,struct.pack('<i',idx));ret=(child0,child1)[idx] if 0<=idx<count else 0
                elif short=='43e11c':ret=1 if hidden and r0==child0 else 0
                elif short=='48b9c0':ret=rtl
                elif short=='48b9fc':ret=1 if name=='row_grow' else 0
                elif short=='43fe16':ret=20
                elif short=='451598':
                    a,b=struct.unpack('<ii',uc.mem_read(r0,12)[0:4]+uc.mem_read(r0+8,4));ret=b-a+1
                elif short=='4515a4':
                    a,b=struct.unpack('<ii',uc.mem_read(r0+4,4)+uc.mem_read(r0+12,4));ret=b-a+1
                elif short=='43fd9e':ret=4
                elif short=='43fdda':ret=3
                elif short=='450b6c':
                    left=struct.unpack('<i',uc.mem_read(r0,4))[0]
                    uc.mem_write(r0+8,struct.pack('<i',left+r1-1))
                elif short=='450b76':
                    top=struct.unpack('<i',uc.mem_read(r0+4,4))[0]
                    uc.mem_write(r0+12,struct.pack('<i',top+r1-1))
                elif short in ('48b982','48b996'):ret=2 if 'cross' in name else 0
                elif short in ('48b98c','48b9a0'):ret=1 if 'cross' in name else 0
                elif short=='48c6d8':
                    s=uc.reg_read(UC_ARM_REG_SP);p=struct.unpack('<I',uc.mem_read(s,4))[0]
                    q=struct.unpack('<I',uc.mem_read(s+4,4))[0]
                    uc.mem_write(p,struct.pack('<i',0));uc.mem_write(q,struct.pack('<i',0))
                r2=uc.reg_read(UC_ARM_REG_R2)
                if short=='48b8f8':
                    prior=bytes(uc.mem_read(r1,16));uc.mem_write(r0,prior)
                    calls.append((short,prior))
                elif short=='48c770':calls.append((short,r0,r1,idx))
                elif short=='48c6d8':calls.append((short,r0,r1,r2,uc.reg_read(UC_ARM_REG_R3)))
                elif short in ('450b6c','450b76'):calls.append((short,r0,r1))
                elif short=='451670':
                    payload=bytes(uc.mem_read(r2,16)) if r1==0x31 else r2
                    calls.append((short,r0,r1,payload))
                elif short=='44035e':calls.append((short,r0,r1,r2,uc.reg_read(UC_ARM_REG_R3)))
                else:calls.append((short,r0 if short in ('44dce2','43e11c','48b9c0','440656','44dca2') else None,
                                   r1 if short=='44dce2' else None))
                uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.emu_start((syms['audio_uart_lv_children_repos_48c14e'] if is_c else 0x48c14e)|1,
                        0x600000,count=3000)
            effect_suffixes=('44dce2','48c770','48c6d8','440656','48b8f8','450b6c',
                             '450b76','451670','44dca2','44035e')
            effects=[c for c in calls if c[0] in effect_suffixes]
            getters=sorted(c for c in calls if c[0] not in effect_suffixes)
            out.append((effects,getters,bytes(u.mem_read(child0+0x14,28)),bytes(u.mem_read(child1+0x14,28)),
                        bytes(u.mem_read(track,28)),bytes(u.mem_read(0x20003800,24)) if name.startswith('row_grow') else None))
        assert out[0]==out[1],(name,out)
    print(f'PASS {len(cases)} compiled-C/native LV flex repos bounded cases')

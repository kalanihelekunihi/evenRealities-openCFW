"""Bounded actual ARM C/native grid item cases with named lower child cuts."""
from pathlib import Path
import re, struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_grid_item.c'
with tempfile.TemporaryDirectory() as td:
    obj=Path(td)/'item.o';shim=Path(td)/'shim.c';elf=Path(td)/'item.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-c',str(SRC),'-o',str(obj)],check=True)
    imports=[x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
    shim.write_text('#include <stdint.h>\n'+''.join(
        'uint32_t '+n+'(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\n'
        for n in imports))
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_basic_item_48cfe0',
                    str(obj),str(shim),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(
        ['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for case in ('hidden','no_col','no_row','plain','reverse','span_two','stretch','move'):
        out=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            item,grid,region=0x20003000,0x20003100,0x20003200
            x,y,w,h=0x20003400,0x20003500,0x20003600,0x20003700
            u.mem_write(grid,struct.pack('<IIII',x,y,w,h))
            for a,values in ((x,(10,30)),(y,(15,25)),(w,(20,25)),(h,(10,15))):
                u.mem_write(a,struct.pack('<ii',*values))
            u.mem_write(region,struct.pack('<iiii',0,0,100,200))
            u.mem_write(item+0x14,struct.pack('<iiii',111 if case=='move' else 110,215,
                                                130 if case=='move' else 129,224))
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,item);u.reg_write(UC_ARM_REG_R1,grid);u.reg_write(UC_ARM_REG_R2,region)
            mapping={(syms[n]&~1 if is_c else (0x440656 if n=='audio_uart_display_size_changed' else int(n.rsplit('_',1)[1],16))):n for n in imports}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
                r2=uc.reg_read(UC_ARM_REG_R2)
                if n.endswith('48c7fc'):
                    prior=bytes(uc.mem_read(r1,16));uc.mem_write(r0,prior)
                    calls.append((n,prior))
                elif n.endswith(('450b6c','450b76')):calls.append((n,r0,r1))
                elif n.endswith('451670'):
                    payload=bytes(uc.mem_read(r2,16)) if r1==0x31 else r2
                    calls.append((n,r0,r1,payload))
                elif n.endswith('44035e'):calls.append((n,r0,r1,r2,uc.reg_read(UC_ARM_REG_R3)))
                else:calls.append((n,r0,r1 if n.endswith(('43e11c','48c8a8','48c87e','48c888','48c86a','48c874','48c82e','48c838')) else None))
                if n.endswith('43e11c'):ret=1 if case=='hidden' else 0
                elif n.endswith('48c9a4'):ret=0 if case=='no_col' else 2 if case in ('span_two','stretch') else 1
                elif n.endswith('48c9ae'):ret=0 if case=='no_row' else 2 if case in ('span_two','stretch') else 1
                elif n.endswith('48c8a8'):ret=1 if case=='reverse' else 0
                elif n.endswith(('48c9b8','48c9c2')):ret=3 if case=='stretch' else 0
                elif n.endswith('451598') or n.endswith('43fd9e'):ret=20
                elif n.endswith('4515a4') or n.endswith('43fdda'):ret=10
                elif n.endswith('450b6c'):
                    left=struct.unpack('<i',uc.mem_read(r0,4))[0]
                    uc.mem_write(r0+8,struct.pack('<i',left+r1-1));ret=0
                elif n.endswith('450b76'):
                    top=struct.unpack('<i',uc.mem_read(r0+4,4))[0]
                    uc.mem_write(r0+12,struct.pack('<i',top+r1-1));ret=0
                else:ret=0
                uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.emu_start((syms['audio_uart_lv_basic_item_48cfe0'] if is_c else 0x48cfe0)|1,
                        0x600000,count=800)
            effect_suffixes=('48c7fc','440656','450b6c','450b76','451670','44dca2','44035e')
            effects=[c for c in calls if c[0].endswith(effect_suffixes) or c[0]=='audio_uart_display_size_changed']
            getters=sorted(c for c in calls if not (c[0].endswith(effect_suffixes) or c[0]=='audio_uart_display_size_changed'))
            out.append((effects,getters,bytes(u.mem_read(item+0x14,24))))
        assert out[0]==out[1],(case,out)
    print('PASS 8 compiled-C/native LV grid item bounded cases')

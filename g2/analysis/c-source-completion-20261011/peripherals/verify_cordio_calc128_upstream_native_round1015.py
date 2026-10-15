#!/usr/bin/env python3
"""Compare pinned upstream Calc128 copies with official Apollo Thumb."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
repo=root.parent;cordio=repo/'third-party/upstream/cordio'
out=root/'build/c-firmware/cordio-calc128-native-round1015';out.mkdir(parents=True,exist_ok=True)
src=cordio/'wsf/sources/util/calc128.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert subprocess.check_output(['git','-C',str(cordio),'rev-parse','HEAD'],text=True).strip()=='3656312d6b73e2a2c1c8b33ee0385bc199dd97e6'
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';shim=td/'memcpy.c'
    shim.write_text('void *memcpy(void *d,const void *s,__SIZE_TYPE__ n) {'
                    'unsigned char *x=d;const unsigned char *y=s;'
                    'for(__SIZE_TYPE__ i=0;i<n;i++)x[i]=y[i];return d;}\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-ffunction-sections','-fdata-sections','-nostdlib','-fno-builtin',
                    '-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,Calc128Cpy',
                    '-Wl,-u,Calc128Cpy64',
                    '-I'+str(root/'config-recovered/cordio/g2-compat-include'),
                    '-I'+str(cordio/'wsf/include'),str(src),str(shim),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    entries={'Calc128Cpy':(0x542a44,16),'Calc128Cpy64':(0x542a52,8)}
    for name,(native,length) in entries.items():
        effects=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,segment in segments:u.mem_write(addr,segment)
            dst=0x20080000;source=0x20080100
            u.mem_write(dst,bytes([0xa5]*32));u.mem_write(source,bytes(range(32)))
            u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,source)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.emu_start((sym[name] if compiled else native)|1,0x600000,count=10000)
            effects.append(bytes(u.mem_read(dst,32)))
        assert effects[0]==effects[1],(name,length)
receipt={'round':1015,'status':'PASS_PINNED_CORDIO_CALC128_NATIVE',
         'component':'Apollo BLE Calc128Cpy and Calc128Cpy64 pinned upstream versus native',
         'upstream_commit':'3656312d6b73e2a2c1c8b33ee0385bc199dd97e6',
         'source':str(src.relative_to(repo)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entries':{name:{'address':hex(addr),'copied_bytes':length} for name,(addr,length) in entries.items()},
         'validation':'Actual compiled upstream Cortex-M4 C versus official native Thumb destination effects',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Only nonoverlapping fixed-size copy effects are compared',
                  'Full utility and image equivalence/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(entries))

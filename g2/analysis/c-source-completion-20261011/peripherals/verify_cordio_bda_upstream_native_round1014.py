#!/usr/bin/env python3
"""Compare pinned upstream BdaIsZeros with official Apollo Thumb."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
repo=root.parent;cordio=repo/'third-party/upstream/cordio'
out=root/'build/c-firmware/cordio-bda-native-round1014';out.mkdir(parents=True,exist_ok=True)
src=cordio/'wsf/sources/util/bda.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert subprocess.check_output(['git','-C',str(cordio),'rev-parse','HEAD'],text=True).strip()=='3656312d6b73e2a2c1c8b33ee0385bc199dd97e6'
with tempfile.TemporaryDirectory() as td:
    td=Path(td);elf=td/'c.elf';shim=td/'memcmp.c'
    shim.write_text('int memcmp(const void *a,const void *b,__SIZE_TYPE__ n) {'
                    'const unsigned char *x=a,*y=b;for(__SIZE_TYPE__ i=0;i<n;i++)'
                    'if(x[i]!=y[i])return (int)x[i]-(int)y[i];return 0;}\n')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-ffunction-sections','-fdata-sections','-nostdlib','-fno-builtin',
                    '-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,BdaIsZeros',
                    '-I'+str(root/'config-recovered/cordio/g2-compat-include'),
                    '-I'+str(cordio/'wsf/include'),str(src),str(shim),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        image=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in image.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in image.get_section_by_name('.symtab').iter_symbols()}
    vectors=[bytes(6),bytes([1,0,0,0,0,0]),bytes([0,0,0,0,0,1]),
             bytes([0xff]*6),bytes([0,0,7,0,0,0])]
    for data in vectors:
        returns=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,segment in segments:u.mem_write(addr,segment)
            u.mem_write(0x20080000,data)
            u.reg_write(UC_ARM_REG_R0,0x20080000);u.reg_write(UC_ARM_REG_SP,0x200ff000)
            u.reg_write(UC_ARM_REG_LR,0x600001)
            u.emu_start((sym['BdaIsZeros'] if compiled else 0x4d2974)|1,0x600000,count=20000)
            returns.append(u.reg_read(UC_ARM_REG_R0)&0xff)
        assert returns[0]==returns[1],(data,returns)
receipt={'round':1014,'status':'PASS_PINNED_CORDIO_BDA_NATIVE',
         'component':'Apollo BLE BdaIsZeros pinned upstream versus native',
         'upstream_commit':'3656312d6b73e2a2c1c8b33ee0385bc199dd97e6',
         'source':str(src.relative_to(repo)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_entry':'0x4d2974','vectors':[v.hex() for v in vectors],
         'validation':'Actual compiled upstream Cortex-M4 C versus official native Thumb return values',
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Only BdaIsZeros and the listed six-byte vectors are compared',
                  'Full utility and image equivalence/hardware proof remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(vectors))

#!/usr/bin/env python3
"""Differential stock/source proof for the bounded 0x41d90e read helper."""
from pathlib import Path
import hashlib, importlib.util, json, struct, sys
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ELF=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/power-read.elf')
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else HERE/'power-read-comparison.json'
image=BLOB.read_bytes(); digest=hashlib.sha256(image).hexdigest()
assert digest=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec=importlib.util.spec_from_file_location('elf_reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
_,segments,symbols=reader.elf_info(ELF)

def run(source,register_id,out_ptr,primask,seed):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    u.mem_map(0x08000000,0x1000);u.mem_map(0x410000,0x25000);u.mem_map(0x10000,0x10000);u.mem_map(0x30000,0x10000)
    u.mem_map(0x20000000,0x40000);u.mem_map(0x40010000,0x1000)
    if source:
        for seg in segments:u.mem_write(seg['address'],seg['data'])
    else:u.mem_write(0x410000,image)
    values=[(seed ^ (i*0x9e3779b9))&0xffffffff for i in range(0xe0)]
    u.mem_write(0x40010000,b''.join(struct.pack('<I',x) for x in values))
    out=0x20001000
    u.mem_write(out,struct.pack('<I',0xa5a5a5a5))
    u.reg_write(a.UC_ARM_REG_R0,register_id);u.reg_write(a.UC_ARM_REG_R1,out if out_ptr else 0)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001)
    u.reg_write(a.UC_ARM_REG_PRIMASK,primask)
    pc=(symbols['opencfw_bl_power_register_read']&~1) if source else 0x41d90e
    done=False
    def hook(cpu,p,size,_):
        nonlocal done
        if p==0x08000000:done=True;cpu.emu_stop()
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(pc|1,0,count=300)
    assert done
    return {'status':u.reg_read(a.UC_ARM_REG_R0),'out':struct.unpack('<I',u.mem_read(out,4))[0],
            'primask':u.reg_read(a.UC_ARM_REG_PRIMASK)}

cases=[]
for rid,valid,irq,seed in [(0,1,0,0),(15,1,1,0x12345678),(223,1,1,0xffffffff),
                            (0,0,0,0),(15,0,1,0xabcdef01),(223,0,0,0x76543210),
                            (224,1,0,0x12345678),(255,1,1,0xffffffff),
                            (224,0,1,0),(0xffffffff,1,0,0x5a5a5a5a)]:
    f={'register_id':rid,'output_nonnull':bool(valid),'primask':irq,'seed':seed}
    stock=run(False,rid,valid,irq,seed);source=run(True,rid,valid,irq,seed)
    assert stock==source,(f,stock,source)
    cases.append({'fixture':f,'result':stock})

body=image[0x41d90e-0x410000:0x41d92c-0x410000]
result={'status':'PASS','cases':len(cases),'stock_sha256':digest,
 'function_range':['0x41d90e','0x41d92c'],'function_bytes':len(body),
 'source_sha256':hashlib.sha256((ROOT/'g2/components/bootloader/initializer_callbacks/startup_power_register_read.c').read_bytes()).hexdigest(),
 'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
 'correspondence':'Exact instruction-derived operation: reject id >=224 with 5; reject null output with 6; otherwise write MMIO[0x40010000 + 4*id] and return 0.',
 'comparisons':cases}
OUT.write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(cases),'power-register-read cases')

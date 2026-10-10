"""Execute bounded original Thumb routines against TLSF mapping geometry."""
from pathlib import Path
import sys, json, struct, hashlib, random, re
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *
out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'g2/workflow/target.json').exists())
raw=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
u.mem_map(0x4cf000,0x2000); u.mem_write(0x4cf000,raw[0x4cf000-0x437fe0:0x4d1000-0x437fe0])
u.mem_map(0x20000000,0x10000); u.mem_map(0x100000,0x1000)
allowed=[(0x4cff6c,0x4cff9a),(0x4cfd66,0x4cfd70),(0x4cfd18,0x4cfd56)]
executed=set()
profile=json.loads((out/'profile.json').read_text())
gnu=(out/'gnu-thumb.txt').read_text()
gnu_calls=[(int(a,16),int(b,16)) for a,b in re.findall(r'^\s*([0-9a-f]+):.*\bbl\s+([0-9a-f]+)',gnu,re.M)]
assert [(c['site']['site_va'],c['site']['target_va']) for c in profile['calls']]==gnu_calls==[(0x4cff84,0x4cfd66)]
def hook(uc,a,size,user):
    if a==0x100000: uc.emu_stop(); return
    assert any(lo<=a and a+size<=hi for lo,hi in allowed),hex(a)
    executed.add(a)
u.hook_add(UC_HOOK_CODE,hook)
cases=set(range(256))
for bit in range(7,32):
    for sl in range(32):
        boundary=(1<<bit)+(sl<<(bit-5))
        for delta in [-1,0,1]:
            if 0<=boundary+delta<=0xffffffff: cases.add(boundary+delta)
rng=random.Random(0x4cff6c)
cases.update(rng.randrange(1<<32) for _ in range(1000)); cases.add(0xffffffff)
for n in sorted(cases):
    saved={r:0x789a0000+i for i,r in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7])}
    for r,v in saved.items():u.reg_write(r,v)
    for r,v in [(UC_ARM_REG_R0,n),(UC_ARM_REG_R1,0x20000100),(UC_ARM_REG_R2,0x20000104),(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x100001)]:u.reg_write(r,v)
    u.emu_start(0x4cff6d,0,count=200)
    fl,sl=struct.unpack('<II',u.mem_read(0x20000100,8))
    expected=(0,n//4) if n<128 else (n.bit_length()-1-6,(n>>(n.bit_length()-1-5))^32)
    assert (fl,sl)==expected,(n,fl,sl,expected)
    assert u.reg_read(UC_ARM_REG_PC)==0x100000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
    assert all(u.reg_read(r)==v for r,v in saved.items())
(out/'validation.json').write_text(json.dumps({'cases':len(cases),'all_passed':True,'seed':'0x4cff6c','inputs_sha256':hashlib.sha256(b''.join(struct.pack('<I',n) for n in sorted(cases))).hexdigest(),'executed_addresses':[hex(a) for a in sorted(executed)],'unicorn_version':__import__('unicorn').__version__,'geometry':{'SL_INDEX_COUNT_LOG2':5,'ALIGN_SIZE_LOG2':2,'SMALL_BLOCK_SIZE':128,'FL_INDEX_SHIFT':7},'scope':'Original function plus both real helpers executed; outputs and ABI checked; no external function mocks. Emulator is an independent operational check, not hardware or whole-allocator verification.'},indent=2)+'\n')
print('PASS',len(cases),'TLSF mapping cases')

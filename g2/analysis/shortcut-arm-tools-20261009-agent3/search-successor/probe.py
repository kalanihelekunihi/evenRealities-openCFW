"""Original-byte mapping_search and caller range checks; no allocator provider mocks."""
from pathlib import Path
import sys,json,struct,hashlib,random,subprocess,dataclasses,re
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import *
from unicorn.arm_const import *
from ablation.analyzers.binary_context import BinaryContext
from ablation.analyzers.func_profiler import FuncProfiler
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'g2/workflow/target.json').exists())
raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
elf=D.parent/'main-analysis-only.elf'
records=json.loads('[]')
for a,b,h in [(0x4cff9a,0x4cffc2,'28f5a5f4c0ce20ce58272435bbb3791fc904e17324a44792ffd7f127ee9a5ab8'),(0x4d0484,0x4d04e6,'c799c8e18bdca28b4c52fa8e0ceec563774f219aa7d1f8d6254a5e3857f94995'),(0x4cff42,0x4cff6c,'e389e5a5f50d7749fe6d0c50b1e40d670ac9cd459739e7af4214dfb37c4e6946'),(0x4cfec2,0x4cfeee,'f394d056140fedcadb44094bfa210ed5a74f4353c204a797fedc59cb24f05de3'),(0x4d0722,0x4d0744,'13a5cfb9e7c0787b215d02f411726522b18926adfcbbfaf4e64c0f73526e8539'),(0x4d0744,0x4d0802,'bf61aff3a89d3499fe24bac533b009e7c24d8e5b6aadf1fed383ef0984f9b94c')]:
    assert sha(raw[a-0x437fe0:b-0x437fe0])==h
    listing=subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-objdump','-D','-M','force-thumb',f'--start-address={a}',f'--stop-address={b}',str(elf)],text=True)
    (D/(hex(a)+'-gnu.txt')).write_text(listing);records.append({'start':hex(a),'end':hex(b),'sha256':h})
ctx=BinaryContext.build(str(elf));ctx.thumb_funcs.add(0x4cff9a)
p=FuncProfiler.from_context(ctx).profile(0x4cff9a,end_va=0x4cffc2)
(D/'profile.json').write_text(json.dumps(dataclasses.asdict(p),indent=2,default=str)+'\n')
assert [(c.site.site_va,c.site.target_va) for c in p.calls]==[(0x4cffaa,0x4cfd66),(0x4cffbc,0x4cff6c)]
assert struct.unpack_from('<I',raw,0x4d06e8-0x437fe0)[0]==0x78f4c8
assert struct.unpack_from('<I',raw,0x4d0854-0x437fe0)[0]==0x78f4c4
assert struct.unpack_from('<II',raw,0x78f4c4-0x437fe0)==(12,0x40000000)
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x10000);u.mem_map(0x100000,0x1000)
mode='';hit=False
def hook(uc,a,size,user):
    global hit
    if a==0x100000:uc.emu_stop();return
    if mode=='locate' and a==0x4cffc2:hit=True;uc.emu_stop();return
    assert any(lo<=a and a+size<=hi for lo,hi in [(0x4cff6c,0x4cffc2),(0x4cfd18,0x4cfd56),(0x4cfd66,0x4cfd70),(0x4d0484,0x4d04e6),(0x4cfec2,0x4cfeee),(0x4cff42,0x4cff6c)]),hex(a)
u.hook_add(UC_HOOK_CODE,hook)
def execute(entry,regs):
    global hit
    hit=False
    for r,v in [(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x100001),(UC_ARM_REG_R3,0x12345678)]+regs:u.reg_write(r,v)
    u.emu_start(entry|1,0,count=300)
def mapping(n):
    rounded=(n+((1<<(n.bit_length()-1-5))-1 if n>=128 else 0))&0xffffffff
    return (0,rounded//4) if rounded<128 else (rounded.bit_length()-1-6,(rounded>>(rounded.bit_length()-1-5))^32)
cases=set(range(256));rng=random.Random(0x4cff9a);cases.update(rng.randrange(1<<32) for _ in range(1000))
for bit in range(7,32):
    for sl in range(32):
        b=(1<<bit)+(sl<<(bit-5))
        cases.update(x for x in [b-1,b,b+1] if 0<=x<=0xffffffff)
cases.update([0x3effffff,0x3f000000,0x3f000001,0x3fffffff,0x40000000,0xfc000000,0xfc000001,0xffffffff])
mode='search'
for n in sorted(cases):
    execute(0x4cff9a,[(UC_ARM_REG_R0,n),(UC_ARM_REG_R1,0x20000100),(UC_ARM_REG_R2,0x20000104)])
    assert struct.unpack('<II',u.mem_read(0x20000100,8))==mapping(n)
    assert u.reg_read(UC_ARM_REG_R0)==0x12345678 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
locate=[];mode='locate'
for n in [0,1,12,127,128,0x3effffff,0x3f000000,0x3f000001,0x3fffffff,0x40000000,0xfc000000,0xfc000001,0xffffffff]:
    execute(0x4d0484,[(UC_ARM_REG_R0,0x20001000),(UC_ARM_REG_R1,n)])
    assert hit==(n!=0 and mapping(n)[0]<24)
    locate.append({'size':hex(n),'mapping':mapping(n),'reached_search_provider':hit})
mode='adjust';adjust=[]
for n in [0,1,11,12,13,0x3ffffff8,0x3ffffffc,0x3ffffffd,0x40000000,0xfffffffc,0xfffffffd,0xfffffffe,0xffffffff]:
    execute(0x4cff42,[(UC_ARM_REG_R0,n),(UC_ARM_REG_R1,4)])
    aligned=(n+3)&0xfffffffc;expected=max(aligned,12) if n and aligned<0x40000000 else 0
    actual=u.reg_read(UC_ARM_REG_R0);assert actual==expected
    adjust.append({'request':hex(n),'adjusted':hex(actual),'below_max_or_zero':actual<0x40000000})
(D/'results.json').write_text(json.dumps({'stock_sha256':sha(raw),'extents':records,'mapping_cases':len(cases),'all_passed':True,'unicorn_version':__import__('unicorn').__version__,'locate_prefix':locate,'adjust':adjust,'constants':{'minimum_block':12,'block_size_max':0x40000000},'scope':'Original mapping_search and helpers; original block_locate prefix stops before search provider; original adjust_request_size plus align_up. No provider mocks.'},indent=2)+'\n')
print('PASS',len(cases),'mapping_search cases,',len(locate),'locate prefixes,',len(adjust),'adjust cases')

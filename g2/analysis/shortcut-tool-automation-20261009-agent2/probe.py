"""Bounded original-byte TLSF control layout/search probe; private output only."""
from pathlib import Path
import hashlib,json,struct,subprocess,dataclasses,sys,random
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import *
from unicorn.arm_const import *
from ablation.analyzers.binary_context import BinaryContext
from ablation.analyzers.func_profiler import FuncProfiler
D=Path(__file__).resolve().parent
R=next(p for p in D.parents if (p/'g2/workflow/target.json').exists())
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
base=0x437fe0
source=R/'g2/analysis/bootloader-completion-2026-10-06/upstream-worker/tlsf/tlsf.c'
assert sha(source.read_bytes())=='2a0f8cfc9cfe6114ccdc6cf22339059440b16f1149b5107bead4ae4c3a0d50e2'
# Authenticate the earlier analysis envelope before copying it privately.
envelope=(R/'g2/analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf').read_bytes()
ph=struct.unpack_from('<8I',envelope,52)
assert ph[0]==1 and ph[2]==base and ph[4]==len(raw)
assert envelope[ph[1]:ph[1]+len(raw)]==raw
elf=D/'private-main-analysis-only.elf';elf.write_bytes(envelope)
scopes=[(0x4d0524,0x4d0554,'fe8b87ca377d49c0c78ca4d30f04a9ba0fcfafa76757f8044ab4689959e454df'),(0x4cffc2,0x4d003a,'c583e2d8b8fad3aebe545bc108c40cd960c3c3486be3aaa11c943de6c1c9a8c9')]
ctx=BinaryContext.build(str(elf));records=[]
for a,b,h in scopes:
    assert sha(raw[a-base:b-base])==h
    ctx.thumb_funcs.add(a)
    profile=FuncProfiler.from_context(ctx).profile(a,end_va=b)
    (D/f'{a:x}-profile.json').write_text(json.dumps(dataclasses.asdict(profile),indent=2,default=str)+'\n')
    listing=subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-objdump','-D','-M','force-thumb',f'--start-address={a}',f'--stop-address={b}',str(elf)],text=True)
    (D/f'{a:x}-gnu.txt').write_text(listing)
    calls=[(c.site.site_va,c.site.target_va) for c in profile.calls]
    expected=[] if a==0x4d0524 else [(0x4cfffa,0x4cfd56),(0x4d001a,0x4d09b4),(0x4d0024,0x4cfd56)]
    assert calls==expected,(calls,expected)
    records.append({'start':a,'end':b,'sha256':h,'calls':calls})
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:])
u.mem_map(0x20000000,0x10000);u.mem_map(0x100000,0x1000)
control=0x20001000;fli=0x20000500;sli=fli+4
mode='';writes=[];assertion=None;visited=set()
allowed=[(a,b) for a,b,_ in scopes]+[(0x4cfd18,0x4cfd66)]
def code(uc,a,n,user):
    global assertion
    if a==0x100000:uc.emu_stop();return
    if a==0x4d09b4:
        assertion=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
        uc.emu_stop();return
    assert any(lo<=a and a+n<=hi for lo,hi in allowed),hex(a)
    visited.add(a)
def write(uc,access,a,n,v,user):
    if control<=a<control+0x1000:writes.append((a-control,n,v))
u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
def execute(entry):
    global assertion
    assertion=None
    for r,v in [(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x100001),(UC_ARM_REG_R0,control),(UC_ARM_REG_R1,fli),(UC_ARM_REG_R2,sli)]:u.reg_write(r,v)
    u.emu_start(entry|1,0,count=12000)
    if assertion is None:assert u.reg_read(UC_ARM_REG_SP)==0x2000f000
def put(a,v):u.mem_write(a,struct.pack('<I',v))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def initialize():
    writes.clear();u.mem_write(control,bytes([0xa5])*0x1000);execute(0x4d0524)
    expected={8:control,12:control,16:0}
    expected.update({20+4*fl:0 for fl in range(24)})
    expected.update({116+128*fl+4*sl:control for fl in range(24) for sl in range(32)})
    assert len(writes)==795 and {o:v for o,n,v in writes}==expected
    assert all(n==4 for o,n,v in writes)
    assert bytes(u.mem_read(control,8))==bytes([0xa5])*8
    assert bytes(u.mem_read(control+3188,0x1000-3188))==bytes([0xa5])*(0x1000-3188)
initialize();construct_writes=list(writes)
tests=[]
def test(fl,sl,maps):
    initialize();bitmap=sum(1<<f for f,m in enumerate(maps) if m)
    put(control+16,bitmap)
    for f,m in enumerate(maps):put(control+20+4*f,m)
    for f in range(24):
        for s in range(32):put(control+116+128*f+4*s,0x21000000+128*f+4*s)
    put(fli,fl);put(sli,sl);writes.clear();execute(0x4cffc2)
    eligible=maps[fl]&((0xffffffff<<sl)&0xffffffff);chosen_fl=fl
    if not eligible:
        higher=bitmap&((0xffffffff<<(fl+1))&0xffffffff)
        if higher:chosen_fl=(higher&-higher).bit_length()-1;eligible=maps[chosen_fl]
    if eligible:
        chosen_sl=(eligible&-eligible).bit_length()-1
        expected=0x21000000+128*chosen_fl+4*chosen_sl
        assert (get(fli),get(sli))==(chosen_fl,chosen_sl)
    else:
        expected=0;assert (get(fli),get(sli))==(fl,sl)
    assert assertion is None and u.reg_read(UC_ARM_REG_R0)==expected
    assert writes==[],writes
    tests.append([fl,sl,maps,expected])
for fl in range(24):
    for sl in range(32):
        maps=[0]*24;maps[fl]=1<<sl;test(fl,sl,maps)
        maps=[0]*24;test(fl,sl,maps)
        if fl<23:
            maps[fl+1]=1<<(31-sl);test(fl,sl,maps)
rng=random.Random(0x4cffc2)
for _ in range(400):test(rng.randrange(24),rng.randrange(32),[rng.getrandbits(32) if rng.randrange(3) else 0 for _ in range(24)])
# Inconsistent bitmap: preserve actual assertion arguments, stop before provider.
initialize();put(control+16,2);put(fli,0);put(sli,0);execute(0x4cffc2)
assert assertion is not None and assertion[2]==568
def cstring(a):
    i=a-base;return raw[i:raw.index(0,i)].decode('utf-8')
assert_data={'arguments':assertion,'expression':cstring(assertion[0]),'file':cstring(assertion[1]),'line':assertion[2],'provider_executed':False}
receipt={'image_sha256':sha(raw),'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(envelope),'mapping':{'payload_offset':'loaded_address - 0x00437fe0','analysis_envelope':'authored metadata, original mapped bytes'},'scopes':records,'construct_write_count':len(construct_writes),'control_extent':3188,'search_case_count':len(tests),'case_sha256':sha(json.dumps(tests,separators=(',',':')).encode()),'all_passed':True,'assertion_boundary':assert_data,'visited_addresses':sorted(visited),'unicorn_version':__import__('unicorn').__version__,'ablation_pin':subprocess.check_output(['git','-C',str(R/'third-party/tools/ablation'),'rev-parse','HEAD'],text=True).strip(),'script_sha256':sha(Path(__file__).read_bytes())}
(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS control initialization 795 writes; search cases',len(tests));print(json.dumps(assert_data))

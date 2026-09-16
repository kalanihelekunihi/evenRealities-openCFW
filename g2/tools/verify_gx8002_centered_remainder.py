# SPDX-License-Identifier: MIT
"""Execute recovered centered remainder over finite values and half ties."""
import json,random,struct,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32,IMAGE,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_fmod_finite import reference


def bits(x):return struct.unpack('<Q',struct.pack('<d',x))[0]
def number(x):return struct.unpack('<d',struct.pack('<Q',x))[0]


def verify():
    path=ROOT/'build/gx8002-centered-remainder/centered.elf'
    report=json.loads((ROOT/'docs/research/gx8002-centered-remainder.json').read_text())
    assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'centered')
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    memory={s['address']+i:b for s in elf.sections if s['flags']&2 and s['size'] and s['type']!=8 for i,b in enumerate(elf.contents(s))}
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    original=Elf32(wrapper.read_bytes(),'stock')
    assert original.contents(next(s for s in original.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x48598','--stop-address=0x4863c',str(wrapper)],text=True))
    # Keep stock helper and fabs instructions; redirect only external calls to
    # the same authenticated source dependencies used by the reconstructed C.
    targets=set()
    for pc,(op,args,width) in list(old.items()):
        if op=='bsr' and not 0x48598<=int(args,16)<0x4863c:
            target=int(args,16);targets.add(target)
            runtime=target-0x3b940+0x10003000
            assert runtime in code
            old[pc]=(op,hex(runtime),width)
    assert targets=={0x495e4,0x4aae0,0x4ab60,0x4a790,0x4a754,0x4a724}
    old.update(code)
    pairs=[(bits(x),bits(p)) for x in (-9.,-7.,-5.,-3.,-1.,-0.,0.,1.,3.,5.,7.,9.) for p in (-2.,2.,4.)]
    rng=random.Random(48596)
    pairs += [(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(400)]
    count=0
    for a,b in pairs:
        if (a>>52)&2047==2047 or (b>>52)&2047==2047 or not b&((1<<63)-1):continue
        r=number(reference(a,b));p=number(b)
        if r>0 and r>p*0.5:r-=p
        if r<0 and -r>p*0.5:r+=p
        actual=execute(code,0x1000fc5c,bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True,readonly=memory,max_steps=100000)
        original=execute(old,0x4859c,bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True,readonly=memory,max_steps=100000)
        assert original==actual,(hex(a),hex(b),hex(original),hex(actual))
        assert actual==bits(r),(hex(a),hex(b),hex(actual),hex(bits(r)))
        count+=1
    special_values=[0,1,0x8000000000000000,0x8000000000000001,
                    bits(1.0),bits(-1.0),0x7ff0000000000000,0xfff0000000000000,
                    0x7ff8000000000000,0xfff8000000000042,
                    0x7ff0000000000001,0xfff0000000000042]
    special_count=0
    for a in special_values:
        for b in special_values:
            args=[a&0xffffffff,a>>32,b&0xffffffff,b>>32]
            actual=execute(code,0x1000fc5c,bytes(20),arguments=args,return_pair=True,readonly=memory,max_steps=100000)
            original=execute(old,0x4859c,bytes(20),arguments=args,return_pair=True,readonly=memory,max_steps=100000)
            assert actual==original,(hex(a),hex(b),hex(actual),hex(original))
            special_count+=1
    result={'special_comparison_cases':special_count,'source_elf_sha256' :report['elf_sha256'],'finite_cases':count,'stock_helper_comparison_cases':count,'stock_sha256':IMAGE_SHA,'comparison_dependency_policy':'Stock helper and fabs instructions; all external arithmetic/fmod calls redirected to the same authenticated source implementations.','oracle':'Exact integer fmod, followed by separately rounded binary64 host comparisons and adjustments. Includes positive/negative periods and exact half ties.','source_admitted':False,'limits':['Finite sampled source execution with ABI checks; Special comparisons cover signed zeros, subnormals, infinities and NaN payloads with shared source dependencies; full-stock dependencies, floating flags/traps and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-centered-remainder-execution.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())

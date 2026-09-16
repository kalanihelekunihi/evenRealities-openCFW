# SPDX-License-Identifier: MIT
"""Execute stock large-angle reduction with shared source dependencies.

This is diagnostic evidence, not an admitted replacement or a full-stock
arithmetic execution claim. Preserve accuracy failures in the report.
"""
import json,subprocess
from decimal import Decimal,localcontext,ROUND_HALF_EVEN
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_centered_remainder import bits,number
from verify_gx8002_reducer_accuracy import pi


def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=Elf32(wrapper.read_bytes(),'stock')
    assert old.contents(next(s for s in old.sections if s['name']=='.data'))==stock
    path=ROOT/'build/gx8002-centered-remainder/centered.elf'
    report=json.loads((ROOT/'docs/research/gx8002-centered-remainder.json').read_text())
    assert sha(path.read_bytes())==report['elf_sha256'];elf=Elf32(path.read_bytes(),'source dependencies')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    source=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x4863c','--stop-address=0x48994',str(wrapper)],text=True))
    code.update(decode(subprocess.check_output([pre,'-D','--start-address=0x48598','--stop-address=0x4859c',str(wrapper)],text=True)))
    targets=set()
    for pc,(op,args,width) in list(code.items()):
        if op=='bsr' and int(args,16)!=0x48598:
            target=int(args,16);targets.add(target)
            runtime=target-0x3b940+0x10003000
            assert runtime in source
            code[pc]=(op,hex(runtime),width)
    code.update(source)
    memory={s['address']+i:b for s in elf.sections if s['flags']&2 and s['size'] and s['type']!=8 for i,b in enumerate(elf.contents(s))}
    memory.update({0x10015508+i:b for i,b in enumerate(stock[0x4de48:0x4ded8])})
    rows=[]
    with localcontext() as ctx:
        ctx.prec=520;halfpi=pi(520)/2
        for value in [1e7,-1e7,1e10,-1e10,1e30,-1e30,1e100,-1e100,1e300,-1e300]:
            raw=bits(value);trace={0x4880e:[]}
            n=execute(code,0x4863c,bytes(20),arguments=[raw&0xffffffff,raw>>32,0x7a00],readonly=memory,trace=trace,max_steps=100000,stack_bytes=2048)
            assert len(trace[0x4880e])==1
            mem=trace[0x4880e][0]['memory'];output=int.from_bytes(bytes(mem[0x7a00+i] for i in range(8)),'little')
            tail=bytes(mem[0x7a08+i] for i in range(8))
            q=(Decimal.from_float(value)/halfpi).to_integral_value(rounding=ROUND_HALF_EVEN)
            remainder=Decimal.from_float(value)-q*halfpi
            actual=number(output)
            rows.append({'input':hex(raw),'output':hex(output),'returned_quotient':n,'reference_quotient_mod4':int(q)%4,'quotient_mod4_matches':n%4==int(q)%4,'absolute_remainder_error':str(abs(Decimal.from_float(actual)-remainder)),'tail_untouched':tail==b'\xa5'*8})
    result={'stock_sha256':IMAGE_SHA,'source_dependencies_elf_sha256':report['elf_sha256'],'redirected_stock_targets':sorted(targets),'cases':rows,'source_admitted':False,'limits':['Stock reducer instruction execution with authenticated shared source arithmetic and centered remainder, not full-stock dependencies.','Only ten finite large-angle samples; report records discrepancies without admitting this algorithm.','Tail sentinel detects absence of output writes on these paths, not all caller initialization behavior.']}
    (ROOT/'docs/research/gx8002-compact-reducer-large.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze();print([(x['input'],x['quotient_mod4_matches'],x['absolute_remainder_error'],x['tail_untouched']) for x in r['cases']])

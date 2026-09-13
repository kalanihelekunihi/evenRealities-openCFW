# SPDX-License-Identifier: MIT
"""Symbolically check a single volatile register read for every returned word."""
import json,re,subprocess
from build_gx8002_distance_noise import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,literals):
    regs={f'r{i}':('initial',i) for i in range(32)};initial=regs.copy();pc=entry;reads=[];visited=[]
    for _ in range(5):
        op,args,width=code[pc];visited.append(pc);parts=[s.strip() for s in args.split(',')]
        if op=='movih':regs[parts[0]]=int(parts[1],0)<<16
        elif op=='lrw':
            assert pc in literals;address,value=literals[pc];assert int(parts[1],0)==value;regs[parts[0]]=value
        elif op=='ld.w':
            dest,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups()
            assert isinstance(regs[base],int);address=regs[base]+int(offset,0)
            assert address==0xa0a001b8 and not reads
            reads.append([address,4]);regs[dest]=('mmio_word',address)
        elif op=='rts':
            assert regs['r0']==('mmio_word',0xa0a001b8)
            assert all(regs[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return {'return':'unchanged arbitrary 32-bit MMIO sample','reads':reads,'instruction_addresses':visited}
        else:raise ValueError((op,args))
        pc+=width
    raise ValueError('No return')

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xdd38','--stop-address=0xdd42',str(p)],text=True))
    p=ROOT/'build/gx8002-distance-noise/noise.elf';elf=Elf32(p.read_bytes(),'noise');s=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(s);entry=s['address']
    assert entry==0x102047ac and len(body)==12
    # Authenticate the short LRW's encoded PC-relative literal address directly.
    half=int.from_bytes(body[:2],'little');assert half==0x1062
    literal_address=(entry&~3)+4*(half&31);assert literal_address==entry+8
    literal=int.from_bytes(body[8:12],'little');assert literal==0xa0a00180
    new=decode(subprocess.check_output([pre,'-d',str(p)],text=True))
    a=execute(old,0xdd38,{});b=execute(new,entry,{entry:(literal_address,literal)})
    assert a['return']==b['return'] and a['reads']==b['reads']==[[0xa0a001b8,4]]
    assert b['instruction_addresses']==[entry,entry+2,entry+4] and body[6:8]==b'\0\0'
    return {'candidate':candidate,'stock_execution':a,'source_execution':b,'literal_address':literal_address,'literal_value':literal,'elf_sha256':sha(p.read_bytes()),'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('build_gx8002_distance_noise.py','verify_gx8002_distance_noise.py','verify_gx8002_memcpy_source.py')},'source_admitted':False,'hardware_qualified':False,'limits':['Restricted symbolic instruction execution proves one word read, unchanged arbitrary return and preserved ABI registers. Literal pool checked against encoded LRW. No helper calls or stores.','No physical audio peripheral measurement; registry admission pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-distance-noise-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Distance-noise symbolic register-read equivalence passed')

# SPDX-License-Identifier: MIT
"""Compare stock packed-DSP reduction and compiled scalar C-SKY output."""
import json,random,re,subprocess
from build_gx8002_backup_maxabs_q15 import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def signed(v,bits=32):
    v&=(1<<bits)-1;return v-(1<<bits) if v&(1<<(bits-1)) else v

def execute(code,entry,values,alias=None):
    count=len(values);memory=bytearray(b'\xa5'*(count*2+12))
    for i,v in enumerate(values):memory[2*i:2*i+2]=(v&65535).to_bytes(2,'little')
    output=0x1000+(2*alias if alias is not None else count*2+4)
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=0x1000,r1=output,r2=count);initial=r.copy();pc=entry;condition=False;reads=0;stores=0
    def read(address,size):
        nonlocal reads
        off=address-0x1000;assert 0<=off and off+size<=count*2;reads+=size
        return int.from_bytes(memory[off:off+size],'little')
    for _ in range(count*20+100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='movi':r[p[0]]=int(p[1],0)
        elif op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='subi':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]-int(p[-1],0))&0xffffffff
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='abs':r[p[0]]=abs(signed(r[p[1]]))
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='max.u32':r[p[0]]=max(r[p[1]],r[p[2]])
        elif op=='pabs.s16.s':
            v=r[p[1]];r[p[0]]=sum(min(abs(signed(v>>(16*i),16)),32767)<<(16*i) for i in range(2))
        elif op=='pmax.u16':
            a,b=r[p[1]],r[p[2]];r[p[0]]=sum(max((a>>(16*i))&65535,(b>>(16*i))&65535)<<(16*i) for i in range(2))
        elif op=='dup.16':r[p[0]]=((r[p[1]]>>(int(p[2])*16))&65535)*0x10001
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op in ('br','bt'):
            if op=='br' or condition:nxt=int(p[0],0)
        elif op=='bloop':
            r[p[0]]=(r[p[0]]-1)&0xffffffff
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('pldbi.d','ldbi.h','ldbi.hs','stbi.h','st.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m,args
            reg,base,offset=m.groups();address=r[base]+(int(offset,0) if offset else 0)
            if op=='pldbi.d':
                r[reg]=read(address,4);r['r'+str(int(reg[1:])+1)]=read(address+4,4);r[base]+=8
            elif op.startswith('ld'):
                value=read(address,2);r[reg]=(signed(value,16)&0xffffffff) if op=='ldbi.hs' else value;r[base]+=2
            else:
                assert address==output and reads==count*2;stores+=1
                off=address-0x1000;memory[off:off+2]=(r[reg]&65535).to_bytes(2,'little')
                if op=='stbi.h':r[base]+=2
        elif op=='rts':
            assert stores==1 and reads==count*2
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return bytes(memory)
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('instruction bound')

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    original=decode(subprocess.check_output([pre,'-D','--start-address=0x47a74','--stop-address=0x47ac0',str(path)],text=True))
    compiled=decode((ROOT/'build/gx8002-backup-maxabs-q15/maxabs.disassembly.txt').read_text());cases=0
    def compare(values,alias=None):
        nonlocal cases
        assert execute(original,0x47a74,values,alias)==execute(compiled,0x1000f134,values,alias),(len(values),alias)
        cases+=1
    for value in range(-32768,32768):compare([value])
    rng=random.Random(76);compare([])
    for count in range(1,258):
        values=[rng.randrange(-32768,32768) for _ in range(count)]
        for alias in (0,count//2,count-1):compare(values,alias)
    result={'build':evidence,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['All Q15 single values plus bounded reductions and aliased output. Complete final memory, all input bytes read, single output write after reads, and callee-saved registers checked.','Scalar and packed loads differ in width; no MMIO/atomicity equivalence. Model evidence, not hardware or full count-domain proof.']}
    (ROOT/'docs/research/gx8002-backup-maxabs-q15-decoded.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['decoded_cases'],'decoded cases')

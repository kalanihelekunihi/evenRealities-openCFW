# SPDX-License-Identifier: MIT
"""Execute finite binary64 unpack instructions from stock and rebuilt GCC."""
import json,re,random,subprocess,struct
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,value):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=0x1000,r1=0x2000,r14=0x3000);initial=r.copy()
    mem={a:0xa5 for a in range(0x2000,0x2014)}
    mem.update({0x1000+i:b for i,b in enumerate(value.to_bytes(8,'little'))});pc=entry;c=False
    for _ in range(1000):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')];n=pc+w
        def v(x):return r[x] if x.startswith('r') else int(x,0)
        if op in ('ld.w','ld.h','ld.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0);size={'ld.w':4,'ld.h':2,'ld.b':1,'st.w':4}[op]
            if op=='st.w':
                assert 0x2000<=a<=0x2010 or a==0x2ffc
                for i,b in enumerate(r[reg].to_bytes(4,'little')):mem[a+i]=b
            else:r[reg]=int.from_bytes(bytes(mem[a+i] for i in range(size)),'little')
        elif op in ('movi','mov','movih'):r[p[0]]=v(p[1])<<(16 if op=='movih' else 0)
        elif op=='zext':r[p[0]]=(v(p[1])>>int(p[3]))&((1<<(int(p[2])-int(p[3])+1))-1)
        elif op=='inct':
            if c:r[p[0]]=(v(p[1])+v(p[2]))&0xffffffff
        elif op=='bclri':r[p[0]]=v(p[1])&~(1<<int(p[2]))
        elif op=='bmaski':r[p[0]]=(1<<int(p[1]))-1
        elif op in ('or','and','nor','addi','subi','lsli','lsri','addc'):
            a=v(p[0] if len(p)==2 else p[1]);b=v(p[-1])
            if op=='addc':total=a+b+int(c);c=total>0xffffffff;result=total
            else:result={'or':lambda:a|b,'and':lambda:a&b,'nor':lambda:~(a|b),'addi':lambda:a+b,'subi':lambda:a-b,'lsli':lambda:a<<b,'lsri':lambda:a>>b}[op]()
            r[p[0]]=result&0xffffffff
        elif op=='add.64':
            def pair(x):i=int(x[1:]);return r[x]|(r[f'r{i+1}']<<32)
            result=(pair(p[1])+pair(p[2]))&0xffffffffffffffff;i=int(p[0][1:]);r[p[0]]=result&0xffffffff;r[f'r{i+1}']=result>>32
        elif op in ('cmpnei','cmphs','cmplt'):
            a,b=v(p[0]),v(p[1]);signed=lambda x:x-(1<<32) if x>>31 else x
            c=a!=b if op=='cmpnei' else a>=b if op=='cmphs' else signed(a)<signed(b)
        elif op in ('bt','bf','br','bez','bnez'):
            take=c if op=='bt' else not c if op=='bf' else True if op=='br' else v(p[0])==0 if op=='bez' else v(p[0])!=0
            if take:n=int(p[-1],0)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15))
            return bytes(mem[a] for a in range(0x2000,0x2014))
        else:raise ValueError((hex(pc),op,args))
        pc=n
    raise ValueError('bound')

def oracle(value):
    sign=value>>63;exponent=(value>>52)&2047;fraction=value&((1<<52)-1)
    words=[0xa5a5a5a5]*5;words[1]=sign
    if exponent==2047:
        words[0]=4 if not fraction else fraction>>51
        if fraction:
            payload=(fraction&((1<<51)-1))<<8;words[3]=payload&0xffffffff;words[4]=payload>>32
    elif not exponent and not fraction:words[0]=2
    else:
        words[0]=3
        if exponent:power=exponent-1023;mantissa=((1<<52)|fraction)<<8
        else:
            shift=53-fraction.bit_length();power=-1022-shift;mantissa=fraction<<(shift+8)
        words[2]=power&0xffffffff;words[3]=mantissa&0xffffffff;words[4]=mantissa>>32
    return struct.pack('<5I',*words)

def verify(placed=False):
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    path=ROOT/'build/gx8002-exp-source-closure/exp.elf';report=json.loads((ROOT/'docs/research/gx8002-exp-source-closure.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    if placed:
        from build_gx8002_backup_double_unpack import build
        report=build();path=ROOT/'build/gx8002-backup-double-unpack/unpack.elf'
        assert sha(path.read_bytes())==report['elf_sha256']
    e=Elf32(path.read_bytes(),'source');entry=next(s['value'] for s in e.symbols() if s['name']=='__unpack_d')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4afd4','--stop-address=0x4b0b8',str(wrapper)],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    values=[(sign<<63)|(exponent<<52)|fraction for sign in (0,1) for exponent in range(2047) for fraction in (0,1,(1<<51),(1<<52)-1)]
    values += [(sign<<63)|(1<<bit) for sign in (0,1) for bit in range(52)]
    finite_count=len(values)
    payloads={0,1,(1<<51),(1<<52)-1}
    payloads.update(1<<i for i in range(52));payloads.update(((1<<52)-1)^(1<<i) for i in range(52))
    rng=random.Random(804);payloads.update(rng.getrandbits(52) for _ in range(4096))
    values += [(sign<<63)|(2047<<52)|p for sign in (0,1) for p in sorted(payloads)]
    vendor=ROOT/'build/upstream-xuantie-qemu-csky/translate_v2.c'
    assert sha(vendor.read_bytes())=='d56e8f41f25c225e3a6d7446a26062cacee2a4f9fe6a2df8661cf066c9e373a5'
    for value in values:assert execute(old,0x4afd4,value)==execute(new,entry,value)==oracle(value),hex(value)
    result={'placed':placed,'stock_sha256':IMAGE_SHA,'source_elf_sha256':sha(path.read_bytes()),'finite_cases':finite_count,'nonfinite_cases':len(values)-finite_count,'instruction_semantics_sha256':sha(vendor.read_bytes()),'source_admitted':False,'limits':['Exact five-word unpack output including untouched fields and callee-save state; finite and sampled NaN/infinity cases agree with independent integer field oracle. Complete pack/arithmetic remain pending.']}
    (ROOT/('docs/research/gx8002-double-unpack-placed.json' if placed else 'docs/research/gx8002-double-unpack.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())

# SPDX-License-Identifier: MIT
"""Compare decoded stock/GCC binary64 parts comparison against numeric ordering."""
import json,re,random,struct,subprocess,math
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_unpack import oracle

def execute(code,entry,a,b):
    r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=0x1000,r1=0x2000);initial=r.copy()
    mem={base+i*4:x for base,body in [(0x1000,oracle(a)),(0x2000,oracle(b))] for i,x in enumerate(struct.unpack('<5I',body))};pc=entry;c=False
    def val(x):return r[x] if x.startswith('r') else int(x,0)
    def signed(x):return x-(1<<32) if x>>31 else x
    for _ in range(100):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')];n=pc+w
        if op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();r[reg]=mem[r[base]+int(off,0)]
        elif op in ('mov','movi'):r[p[0]]=val(p[1])
        elif op in ('subi','subu'):r[p[0]]=(val(p[0] if len(p)==2 else p[1])-val(p[-1]))&0xffffffff
        elif op in ('cmpnei','cmpne','cmphs','cmplt'):
            x,y=val(p[0]),val(p[1]);c=x!=y if op in ('cmpnei','cmpne') else x>=y if op=='cmphs' else signed(x)<signed(y)
        elif op in ('inct','incf'):
            if c==(op=='inct'):r[p[0]]=(val(p[1])+val(p[2]))&0xffffffff
        elif op in ('bt','bf','br'):
            if op=='br' or c==(op=='bt'):n=int(p[0],0)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15))
            return signed(r['r0'])
        else:raise ValueError((hex(pc),op,args))
        pc=n
    raise ValueError('bound')

def verify(placed=False):
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    path=ROOT/'build/gx8002-exp-source-closure/exp.elf';report=json.loads((ROOT/'docs/research/gx8002-exp-source-closure.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    if placed:
        from build_gx8002_backup_double_compare import build
        report=build();path=ROOT/'build/gx8002-backup-double-compare/compare.elf'
        assert sha(path.read_bytes())==report['elf_sha256']
    e=Elf32(path.read_bytes(),'source');entry=next(s['value'] for s in e.symbols() if s['name']=='__fpcmp_parts_d')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4b0b8','--stop-address=0x4b17a',str(wrapper)],text=True));new=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    edges=[(s<<63)|(e<<52)|f for s in (0,1) for e in (0,1,1022,1023,1024,2046,2047) for f in (0,1,(1<<51),(1<<52)-1)]
    pairs=[(a,b) for a in edges for b in edges];rng=random.Random(804)
    pairs += [(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(20000)]
    pairs += [(a,a) for a in edges]
    for a,b in pairs:
        x,y=[struct.unpack('<d',v.to_bytes(8,'little'))[0] for v in (a,b)]
        expected=1 if math.isnan(x) or math.isnan(y) else (x>y)-(x<y)
        assert execute(old,0x4b0b8,a,b)==execute(new,entry,a,b)==expected,(hex(a),hex(b))
    result={'placed':placed,'stock_sha256':IMAGE_SHA,'source_elf_sha256':sha(path.read_bytes()),'cases':len(pairs),'source_admitted':False,'limits':['Canonical unpacked fields from independent integer oracle; decoded parts comparator only, not public comparison wrappers or complete arithmetic. NaN unordered result is +1.']}
    (ROOT/('docs/research/gx8002-double-compare-parts-placed.json' if placed else 'docs/research/gx8002-double-compare-parts.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())

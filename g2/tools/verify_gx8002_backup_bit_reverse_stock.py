# SPDX-License-Identifier: MIT
"""Decoded permutation comparison using pinned vendor loop semantics."""
import hashlib,json,re,subprocess,random
from build_gx8002_backup_bit_reverse import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,entries,table,values,max_pairs=128):
    memory={};events=[]
    def put(a,v,n):
        for i in range(n):memory[a+i]=(v>>(8*i))&255
    for i,v in enumerate(values):put(0x1000+i*4,v,4)
    for i,v in enumerate(table):put(0x4000+i*2,v,2)
    r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=0x1000,r1=entries,r2=0x4000,r14=0x9000)
    initial=r.copy();pc=entry;saved=None;pairs=0
    for _ in range(max_pairs*24+20):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r6';saved={k:r[k] for k in ('r4','r5','r6')};r['r14']-=12
        elif op=='pop':
            assert args=='r4-r6' and r['r14']==0x8ff4;r.update(saved);r['r14']+=12
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','lsri','addu'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a>>b if op=='lsri' else a+b)&0xffffffff
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('ld.h','ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0);n=2 if op=='ld.h' else 4
            if op.startswith('ld'):
                v=sum(memory[a+i]<<(8*i) for i in range(n));r[reg]=v;events.append(('read',a,n,v))
            else:
                assert all(a+i in memory for i in range(n));put(a,r[reg],n);events.append(('write',a,n,r[reg]))
        elif op in ('bnezad','bloop'):
            # Vendor translate_v2.c: subtract one at target width, branch if nonzero.
            r[p[0]]=(r[p[0]]-1)&0xffffffff;pairs+=1
            if r[p[0]]:
                if pairs==max_pairs:return events,'prefix',pairs
                nxt=int(p[1],0)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return events,'return',pairs
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('bound')

def verify():
    evidence=build();manifest=json.loads((ROOT/'docs/research/gx8002-csky-dsp-upstream-evidence.json').read_text())
    row=next(x for x in manifest['files'] if x['file']=='translate_v2.c')
    vendor=(ROOT/'build/upstream-xuantie-qemu-csky/translate_v2.c').read_bytes();assert sha(vendor)==row['sha256']
    assert hashlib.sha1(b'blob '+str(len(vendor)).encode()+b'\0'+vendor).hexdigest()==row['git_blob']
    loop=vendor.decode().split('case 0xe: /* bloop */')[1].split('case 0xf:')[0]
    assert 'tcg_gen_subi_tl(cpu_R[rx], cpu_R[rx], 1);' in loop and 'branch32(ctx, TCG_COND_NE, rx, val);' in loop
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x48164','--stop-address=0x4818a',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-bit-reverse/reverse.disassembly.txt').read_text())
    rng=random.Random(48164);cases=0;prefixes=0
    for entries in (*range(1,257),0,0xffffffff):
      for variant in range(4):
        values=[rng.getrandbits(32) for _ in range(256)]
        # Includes self swaps, duplicates, zero indices and nonzero low offset bits.
        table=[(rng.randrange(256)*8+(variant&1)) if variant<2 else (i%256)*8 if variant==2 else 0 for i in range(256)]
        a=execute(old,0x48164,entries,table,values);b=execute(new,0x1000f824,entries,table,values)
        assert a==b,(entries,variant,a,b)
        assert a[1]==('prefix' if entries in (0,0xffffffff) else 'return')
        assert a[2]==(128 if entries in (0,0xffffffff) else (entries+1)//2)
        if a[1]=='prefix':prefixes+=1
        cases+=1
    report={'build':evidence,'vendor_evidence':manifest,'cases':cases,'bounded_nontermination_prefixes':prefixes,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded stock/C ordered memory trace and ABI comparison, counts 1..256; count 0 and UINT_MAX compare only 128-pair prefixes, not full wrap execution.','Vendor emulator decrement/branch semantics are reference evidence, not hardware qualification. C candidate still exceeds original leaf envelope.']}
    (ROOT/'docs/research/gx8002-backup-bit-reverse-stock-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])

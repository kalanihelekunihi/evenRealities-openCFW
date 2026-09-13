# SPDX-License-Identifier: MIT
"""Execute complete relocated source packer, including its actual shift bodies."""
import json,struct,random,re,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_unpack import oracle as unpack

def execute(code,entry,parts,arguments=None,return_pair=False,readonly=None,trace=None,max_steps=1600,return_float=False,float_arguments=None,float_operation=None):
    r={f'r{i}':0x65430000+i for i in range(32)};r.update(r0=0x1000,r14=0x8000,r15=0xffffffff)
    if arguments is not None:r.update({f'r{i}':x for i,x in enumerate(arguments)})
    initial=r.copy();fr={f'fr{i}':x for i,x in enumerate(float_arguments or [])}
    mem={a:0xa5 for a in range(0x7f00,0x8000)};mem.update({0x1000+i:b for i,b in enumerate(parts)});pc=entry;c=False
    if readonly:
        assert not (mem.keys() & readonly.keys())
        mem.update(readonly)
    def v(x):return r[x] if x.startswith('r') else int(x,0)
    def signed(x):return x-(1<<32) if x>>31 else x
    def pair(x):return r[x]|r['r'+str(int(x[1:])+1)]<<32
    def setpair(x,value):r[x]=value&0xffffffff;r['r'+str(int(x[1:])+1)]=(value>>32)&0xffffffff
    def load(a):return int.from_bytes(bytes(mem[a+i] for i in range(4)),'little')
    def store(a,x):
        assert 0x7f00<=a<0x8000
        for i,b in enumerate(x.to_bytes(4,'little')):mem[a+i]=b
    for _ in range(max_steps):
        if trace is not None and pc in trace:
            trace[pc].append({'registers':r.copy(),'memory':mem.copy()})
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')];n=pc+w
        if op in ('push','pop'):
            regs=[]
            for item in p:
                if '-' in item:
                    a,b=item.split('-');regs += [f'r{i}' for i in range(int(a[1:]),int(b[1:])+1)]
                else:regs.append(item)
            if op=='push':
                r['r14']-=4*len(regs)
                for i,reg in enumerate(regs):store(r['r14']+i*4,r[reg])
            else:
                for i,reg in enumerate(regs):r[reg]=load(r['r14']+i*4)
                r['r14']+=4*len(regs)
                n=r['r15']
        elif op in ('ldbi.b','stbi.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args);assert m
            reg,base=m.groups();address=r[base]
            if op=='ldbi.b':r[reg]=mem[address]
            else:
                assert 0x7f00<=address<0x8000
                mem[address]=r[reg]&255
            r[base]=(r[base]+1)&0xffffffff
        elif op in ('fmuls','fadds','fsubs','fdivs'):
            assert float_operation is not None, 'floating arithmetic model required'
            fr[p[0]]=float_operation(op,fr[p[1]],fr[p[2]])
        elif op=='fmacs':
            assert float_operation is not None, 'floating arithmetic model required'
            # Pass the original accumulator explicitly; the callback owns FP policy.
            fr[p[0]]=float_operation(op,fr[p[1]],fr[p[2]],fr[p[0]])
        elif op=='flds':
            m=re.fullmatch(r'(fr\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();fr[reg]=load(r[base]+int(off,0))
        elif op=='fsts':
            m=re.fullmatch(r'(fr\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();store(r[base]+int(off,0),fr[reg])
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();store(r[base]+int(off,0),r[reg])
        elif op in ('ld.b','ld.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();address=r[base]+int(off,0);size=1 if op=='ld.b' else 2
            r[reg]=int.from_bytes(bytes(mem[address+i] for i in range(size)),'little')
        elif op=='bclri':r[p[0]]=v(p[0] if len(p)==2 else p[1])&~(1<<int(p[-1]))
        elif op in ('ldr.w','ldr.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args);assert m
            reg,base,index,shift=m.groups();address=(r[base]+(r[index]<<int(shift)))&0xffffffff;r[reg]=load(address) if op=='ldr.w' else mem[address]
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();r[reg]=load(r[base]+int(off,0))
        elif op in ('mov','movi','movih','lrw'):r[p[0]]=v(p[1])<<(16 if op=='movih' else 0)
        elif op=='zext':r[p[0]]=(v(p[1])>>int(p[3]))&((1<<(int(p[2])-int(p[3])+1))-1)
        elif op=='andn':r[p[0]]=v(p[0] if len(p)==2 else p[1])&(~v(p[-1])&0xffffffff)
        elif op=='asr':r[p[0]]=(signed(v(p[0] if len(p)==2 else p[1]))>>min(v(p[-1])&63,31))&0xffffffff
        elif op=='asri':r[p[0]]=(signed(v(p[0] if len(p)==2 else p[1]))>>int(p[-1]))&0xffffffff
        elif op=='abs':r[p[0]]=abs(signed(v(p[1])))&0xffffffff
        elif op=='zexth':r[p[0]]=v(p[1])&65535
        elif op=='divu':
            assert v(p[-1])!=0, 'zero divisor requires separate exception qualification'
            r[p[0]]=v(p[0] if len(p)==2 else p[1])//v(p[-1])
        elif op=='mult':r[p[0]]=(v(p[0] if len(p)==2 else p[1])*v(p[-1]))&0xffffffff
        elif op=='mula.32.l':r[p[0]]=(v(p[0])+v(p[1])*v(p[2]))&0xffffffff
        elif op=='zextb':r[p[0]]=v(p[1])&255
        elif op=='ff1':r[p[0]]=32-v(p[1]).bit_length()
        elif op=='btsti':c=bool(v(p[0])&(1<<int(p[1])))
        elif op in ('inct','incf','decf'):
            if c==(op=='inct'):r[p[0]]=(v(p[1])+(-v(p[2]) if op=='decf' else v(p[2])))&0xffffffff
        elif op=='ins':
            high,low=int(p[2]),int(p[3]);mask=((1<<(high-low+1))-1)<<low
            r[p[0]]=(r[p[0]]&~mask)|((v(p[1])<<low)&mask)
        elif op=='subc':
            a,b=v(p[0] if len(p)==2 else p[1]),v(p[-1]);total=a-b-int(not c)
            r[p[0]]=total&0xffffffff;c=total>=0
        elif op=='addc':
            total=v(p[0] if len(p)==2 else p[1])+v(p[-1])+int(c);r[p[0]]=total&0xffffffff;c=total>0xffffffff
        elif op=='bmaski':r[p[0]]=(1<<int(p[1]))-1
        elif op in ('mvc','mvcv'):r[p[0]]=int(c if op=='mvc' else not c)
        elif op in ('or','ori','nor','and','andi','andni','xor','xori','addi','addu','subi','subu','lsli','lsri','lsl','lsr'):
            a=v(p[0] if len(p)==2 else p[1]);b=v(p[-1])
            if op in ('lsl','lsr'):
                b &= 63
                if b>=32:r[p[0]]=0;pc=n;continue
            if op in ('lsli','lsri'):assert b<32
            result=(a|b if op in ('or','ori') else ~(a|b) if op=='nor' else a&~b if op=='andni' else a^b if op in ('xor','xori') else a&b if op in ('and','andi') else a+b if op in ('addi','addu') else a-b if op in ('subi','subu') else a<<b if op in ('lsl','lsli') else a>>b)
            r[p[0]]=result&0xffffffff
        elif op in ('mul.u32','mula.u32'):setpair(p[0],v(p[1])*v(p[2])+(pair(p[0]) if op=='mula.u32' else 0))
        elif op in ('add.64','sub.64'):setpair(p[0],pair(p[1])+(pair(p[2]) if op=='add.64' else -pair(p[2])))
        elif op in ('cmphsi','cmphs','cmpnei','cmpne','cmplt','cmplti'):
            a,b=v(p[0]),v(p[1]);c=a>=b if op in ('cmphsi','cmphs') else a!=b if op in ('cmpnei','cmpne') else signed(a)<signed(b)
        elif op in ('bt','bf','br','bez','bnez','bhz','bhsz','blz','blsz'):
            take=c if op=='bt' else not c if op=='bf' else True if op=='br' else v(p[0])==0 if op=='bez' else v(p[0])!=0 if op=='bnez' else signed(v(p[0]))<=0 if op=='blsz' else signed(v(p[0]))<0 if op=='blz' else signed(v(p[0]))>=0 if op=='bhsz' else signed(v(p[0]))>0
            if take:n=int(p[-1],0)
        elif op=='bnezad':
            r[p[0]]=(v(p[0])-1)&0xffffffff
            if r[p[0]]:n=int(p[1],0)
        elif op=='fmfvrl':r[p[0]]=fr[p[1]]
        elif op=='fmtvrl':fr[p[0]]=v(p[1])
        elif op=='bseti':r[p[0]]=v(p[0] if len(p)==2 else p[1])|(1<<int(p[-1]))
        elif op=='bsr':r['r15']=n;n=int(args,0)
        elif op=='rts':n=r['r15']
        else:raise ValueError((hex(pc),op,args))
        if n==0xffffffff:
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15))
            assert bytes(mem[0x1000+i] for i in range(20))==parts
            if return_float:return fr['fr0']
            return r['r0'] if arguments is not None and not return_pair else pair('r0')
        pc=n
    raise ValueError('bound')

def verify():
    path=ROOT/'build/gx8002-double-core-layout/core.elf';report=json.loads((ROOT/'docs/research/gx8002-double-core-layout.json').read_text());assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'core');entry=next(s['value'] for s in elf.symbols() if s['name']=='__pack_d')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    values=[(s<<63)|(e<<52)|f for s in (0,1) for e in range(2048) for f in (0,1,1<<51,(1<<52)-1)]
    rng=random.Random(804);values += [rng.getrandbits(64) for _ in range(10000)]
    for value in values:
        expected=value
        if ((value>>52)&2047)==2047 and value&((1<<52)-1):expected|=1<<51
        assert execute(code,entry,unpack(value))==expected,hex(value)
    result={'source_elf_sha256':sha(path.read_bytes()),'roundtrip_cases':len(values),'source_admitted':False,'hardware_qualified':False,'limits':['Complete decoded source pack/shift execution from independently unpacked binary64 fields. NaNs expected quieted; input/callee-save preservation checked.', 'Round trips do not cover arithmetic guard/sticky rounding residues or stock pack equivalence.']}
    (ROOT/'docs/research/gx8002-double-pack-target.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())

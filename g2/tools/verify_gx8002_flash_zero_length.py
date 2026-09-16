# SPDX-License-Identifier: MIT
"""Execute cached and failed-identification zero-length flash-reader paths."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def verify(source=False):
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([tool,'-D','--start-address=0x39930','--stop-address=0x39b78',str(wrapper)],text=True));cases=0
    if source:
        from build_gx8002_stage1_flash_read import build
        build()
        candidate=ROOT/'build/gx8002-stage1-flash-read/flash.elf'
        code=decode(subprocess.check_output([tool,'-d',str(candidate)],text=True))
    for device,id_failure in ((0,0),(0x854012,0),(0x1c3812,0),(0xffffffff,0),(0xffffff,1),(0xffffff,0xffffffff)):
      for busy in (0,1,4,16):
       for seed in (0,0x87654321):
        r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};r.update(r0=0x12345678,r1=0x20000000,r2=0,r14=0x20040000)
        initial=dict(r);mem={0x20001730:device};pc=0x10000fdc if source else 0x39930;trace=[];polls=0;condition=False;frames=[]
        for _ in range(250):
            op,args,width=code[pc];p=[a.strip() for a in args.split(',')];nxt=pc+width
            if op=='push':
                registers=[]
                for part in p:
                    if '-' in part:
                        first,last=part.split('-');registers.extend(f'r{i}' for i in range(int(first[1:]),int(last[1:])+1))
                    else:registers.append(part)
                frames.append({k:r[k] for k in registers});r['r14']-=4*len(registers)
            elif op=='pop':
                saved=frames.pop();r.update(saved);r['r14']+=4*len(saved)
                if frames:nxt=r['r15']
                else:
                    assert all(r[k]==initial[k] for k in (*saved,'r14')) and r['r0']==0
                    break
            elif op in ('lrw','movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
            elif op=='bseti':r[p[0]]=r[p[-2]]|1<<int(p[-1],0)
            elif op=='rotli':
                value=r[p[1]];shift=int(p[2],0);r[p[0]]=((value<<shift)|(value>>(32-shift)))&0xffffffff
            elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
            elif op=='addu':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+r[p[-1]])&0xffffffff
            elif op=='mov':r[p[0]]=r[p[1]]
            elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
            elif op in ('addi','subi'):
                a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0);r[p[0]]=a-b if op=='subi' else a+b
            elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
            elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
            elif op in ('bf','bt','bez','bnez'):
                take=(condition if op=='bt' else not condition) if op in ('bt','bf') else (r[p[0]]==0)==(op=='bez')
                if take:nxt=int(p[-1],0)
            elif op in ('ld.w','ld.b','st.w'):
                m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
                reg,base,off=m.groups();address=r[base]+int(off,0)
                if op=='st.w':mem[address]=r[reg];trace.append(['write',address,r[reg]])
                else:r[reg]=mem[address]
            elif op=='bsr':
                target=int(args,0)
                if source and target in code:
                    r['r15']=nxt;pc=target;continue
                if source:target={0x100001f8:0x38b4c,0x10000edc:0x39830}[target]
                if target==0x38b4c:
                    assert r['r0']==13;trace.append(['gate',13,r['r1']])
                elif target==0x39830 and r['r0']==159:
                    assert device==0xffffff and r['r2']==3;trace.append(['identify',159,3])
                else:
                    assert target==0x39830 and r['r0']==5 and r['r2']==1
                    mem[r['r1']]=1 if polls<busy else 0;polls+=1;trace.append(['status',5])
                for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
                if target==0x39830 and trace[-1][0]=='identify':r['r0']=id_failure
            else:raise AssertionError((hex(pc),op,args))
            pc=nxt
        else:raise AssertionError('bound')
        setup=[['write',0xa0300090,1],['write',0xa2000008,0],['write',0xa200002c,0],['write',0xa20000f0,1],['write',0xa2000014,2],['write',0xa200001c,31],['write',0xa2000008,1],['identify',159,3]] if device==0xffffff else []
        assert trace==[['gate',13,1]]+setup+[['status',5]]*(busy+1)+[['gate',13,0]],trace
        assert not any(0x20000000<=a<0x20001000 for a in mem)
        cases+=1
    return {'cases':cases,'stock_sha256':IMAGE_SHA,'source_reader':source,'candidate_sha256':sha(candidate.read_bytes()) if source else None,'destination_writes':0,'limits':['Cached flash IDs and sentinel initialization with failed ID-read returns only; successful ID detection/configuration remains untested. Status helper and gate bodies modeled. Zero length still enables the clock, polls readiness, and disables the clock; it is not a side-effect-free call. No physical timing or nonzero transfer qualification.']}


if __name__=='__main__':
    import sys
    source='--source' in sys.argv
    r=verify(source);(ROOT/('docs/research/gx8002-stage1-flash-zero-length-source.json' if source else 'docs/research/gx8002-flash-zero-length.json')).write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'zero-length flash cases passed')

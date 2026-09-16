# SPDX-License-Identifier: MIT
"""Compare complete stock/source loader control with symbolic flash calls."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_loader import build
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff


def execute(code,entry,helper,base,mode,header,helper_result,seed,payload_observer=None):
    r={f'r{i}':(seed+i*0x10203)&MASK for i in range(32)};r['r14']=0x2002fffc;initial=dict(r)
    mem={0x20001724:base,0x20033ffc:mode};trace=[];saved=None;pc=entry;condition=False;count=0
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            names=['r4','r15'] if args=='r4, r15' else ['r4','r5','r15'];assert args in ('r4, r15','r4-r5, r15')
            saved={n:r[n] for n in names};r['r14']-=4*len(names)
        elif op=='pop':
            r.update(saved);r['r14']+=4*len(saved)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],trace
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='rotli':
            v=r[p[1]];n=int(p[2],0);r[p[0]]=((v<<n)|(v>>(32-n)))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op in ('addi','subi','addu','subu'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a-b if op in ('subi','subu') else a+b)&MASK
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):nxt=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base_reg,off=m.groups();address=(r[base_reg]+int(off,0))&MASK
            if op=='ld.w':r[reg]=mem[address]
            else:
                assert address==0x2002d3e4;mem[address]=r[reg];trace.append(['store_entry',r[reg]])
        elif op=='bsr':
            assert int(args,0)==helper
            count+=1
            if count==1:
                assert r['r2']==4 and r['r1']==r['r14'];mem[r['r1']]=header
                trace.append(['read_header',r['r0'],4])
            else:
                trace.append(['read_payload',r['r0'],r['r1'],r['r2']])
                if payload_observer is not None:payload_observer(r['r0'],r['r1'],r['r2'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xdead0000^i)&MASK
            r['r0']=helper_result
        elif op=='jsr':
            trace.append(['entry',r[args]])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xbeef0000^i)&MASK
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('loader bound')


def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x396a0','--stop-address=0x39724',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-loader/loader.linked.disassembly.txt').read_text());cases=0
    for base,mode,header,result,seed in product((0,0x2f3b0,0xfffffff0),(0,1,MASK,0xaabbccdd),(0,4,0x1408c,MASK),(0,1,MASK),(0,0x87654321)):
        a=execute(old,0x396a0,0x39930,base,mode,header,result,seed)
        b=execute(new,evidence['entry_address'],evidence['helper_address'],base,mode,header,result,seed)
        assert a==b
        special=mode==0xaabbccdd;entry=0x10000100 if special else 0x10003100
        expected=[['read_header',(base+(0x323b0 if special else 0x3000))&MASK,4],['read_payload',(header+0x323b4 if special else base+0x3000+header+4)&MASK,0x20000000 if special else 0x10003000,0 if special else 0x1408c],['store_entry',entry],['entry',entry]]
        assert b==(0,expected);cases+=1
    from analyze_g2_codec_stage2_sections import SEG2_OFF
    current=ROOT/'build/gx8002-fft-q15-clock-integration-experiment'
    image=(current/'firmware_codec.unadmitted.bin').read_bytes()
    report=json.loads((current/'build-report.json').read_text());assert sha(image)==report['firmware_sha256']
    loaded_cases=0
    for mode,seed in product((0,1,MASK,0xaabbccdc),(0,91,MASK)):
        outputs=[]
        for instructions,entry,helper in ((old,0x396a0,0x39930),(new,evidence['entry_address'],evidence['helper_address'])):
            transferred=[]
            def transfer(offset,destination,length):
                assert destination==0x10003000 and length==0x1408c
                body=image[SEG2_OFF+offset:SEG2_OFF+offset+length]
                assert len(body)==length;transferred.append(body)
            header=int.from_bytes(image[SEG2_OFF+0x323b0:SEG2_OFF+0x323b4],'little')
            execute(instructions,entry,helper,0x2f3b0,mode,header,0,seed,transfer)
            assert len(transferred)==1;outputs.append(transferred[0])
        assert outputs[0]==outputs[1]==image[0x3b940:0x4f9cc]
        loaded_cases+=1
    return {'full_image_transfer_cases':loaded_cases,'composed_firmware_sha256':sha(image),'cases':cases,'build':evidence,'limits':['Complete decoded loader control, call arguments, offset wraparound, ignored helper results and ABI checked. First read supplies a header even on modeled failure; failed reads leaving it uninitialized are outside this corpus. Flash transfer and called entry effects are modeled. Integration and hardware qualification pending.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-loader-source-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'stock/source loader cases passed')

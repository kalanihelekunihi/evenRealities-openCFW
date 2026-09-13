# SPDX-License-Identifier: MIT
"""Authenticate observed RFFT callers and their descriptor argument slices."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4f9cc',str(wrapper)],text=True))
    calls=[pc for pc,(op,args,_) in code.items() if op=='bsr' and int(args,0)==0x478a4]
    assert calls==[0x45d1c,0x465b2,0x4e716,0x4edbe]
    specs=[(0x45d1c,0x45cc0,'r3',0x45cca,8,0x45d1a,0x20017020),
           (0x465b2,0x464f4,'r3',0x46500,16,0x465b0,0x2001700c),
           (0x4e716,0x4e714,'r0',None,None,None,0x20017020),
           (0x4edbe,0x4edbc,'r0',None,None,None,0x2001700c)]
    def instruction(pc,op,args):
        actual=code[pc];assert actual[:2]==(op,args),(hex(pc),actual,op,args)
    rows=[]
    for call,load,reg,store,slot,reload,address in specs:
        instruction(load,'lrw',f'{reg}, {address:#x}')
        evidence=[load]
        if store is not None:
            instruction(store,'st.w',f'{reg}, (r14, {slot:#x})')
            instruction(reload,'ld.w',f'r0, (r14, {slot:#x})')
            # No intervening local store to the saved argument slot or local SP
            # change. Callee side effects are explicitly outside this slice.
            for pc,(op,args,width) in code.items():
                if store<pc<reload:
                    assert not (op.startswith('st') and f'(r14, {slot:#x})' in args),(hex(pc),op,args)
                    assert not (args.startswith('r14,') and op in ('mov','addi','subi','addu','subu'))
            evidence += [store,reload]
        instruction(call,'bsr','0x478a4');evidence.append(call)
        rows.append({'call':call,'descriptor':address,'instructions':[{'pc':pc,'operation':code[pc][0],'arguments':code[pc][1]} for pc in evidence],
                     'scope':'Straight-line/local stack slice; intervening callees and unusual control-flow entry are not modeled.' if store else 'Descriptor literal immediately precedes call.'})
    path=ROOT/'build/gx8002-placed-rfft-cluster/cluster.elf';placed=Elf32(path.read_bytes(),'placed')
    symbols={s['name']:s['value'] for s in placed.symbols() if s['name']}
    def read(address,size):
        section=next(s for s in placed.sections if s['flags']&2 and s['address']<=address and address+size<=s['address']+s['size'])
        off=address-section['address'];return placed.contents(section)[off:off+size]
    assert symbols['source_rfft_forward']==0x20017020 and symbols['source_rfft_inverse']==0x2001700c
    cfft=symbols['source_cfft_256'];assert cfft==0x100143e4
    d=read(cfft,16);assert int.from_bytes(d[:2],'little')==256 and int.from_bytes(d[8:12],'little')==0 and int.from_bytes(d[12:14],'little')==240
    for name,flag in [('source_rfft_forward',0),('source_rfft_inverse',1)]:
        d=read(symbols[name],20)
        assert int.from_bytes(d[:4],'little')==512 and d[4:6]==bytes([flag,1]) and int.from_bytes(d[16:20],'little')==cfft
    report={'stock_sha256':IMAGE_SHA,'placed_elf_sha256':sha(path.read_bytes()),'observed_callers':rows,'fixed_descriptors_checked':3,'source_admitted':False,'limits':['Observed direct calls and typed linked descriptors support the CFFT256 specialization.','Does not prove absence of computed callers, descriptor mutation through aliases, or callee writes to saved caller stack slots. Execution permission and full firmware composition remain separate.']}
    (ROOT/'docs/research/gx8002-placed-fft-callers.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(len(analyze()['observed_callers']),'caller slices verified')

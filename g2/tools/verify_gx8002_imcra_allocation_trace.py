# SPDX-License-Identifier: MIT
"""Execute stock allocation instructions independently of the drafted C layout."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,capacity,source=False):
    base=0x20010000;r={f'r{i}':0 for i in range(32)}
    r.update(r4=base,r5=capacity if source else capacity-196,r7=base+196)
    memory={base+12:512,base+20:256,base+16:512,base+28:257};writes=[];pc=0x1000e426 if source else 0x46d68;condition=False
    for _ in range(400):
        if pc==(0x1000e764 if source else 0x47038):return {'success':False,'writes':writes}
        if pc==(0x1000e56a if source else 0x46e9a):return {'success':True,'writes':writes,'end_offset':writes[-1][1]+1028}
        op,args,width=code[pc];p=[a.strip() for a in args.split(',')];nxt=pc+width
        if op=='ld.w' or op=='st.w':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(0x[0-9a-f]+|\d+)\)',args);assert m,args
            reg,addr,offset=m.groups();address=r[addr]+int(offset,0)
            if op=='ld.w':r[reg]=memory[address]
            else:memory[address]=r[reg];writes.append((address-base,r[reg]-base))
        elif op in ('addu','subu','lsli','addi','subi'):
            a=r[p[0]] if len(p)==2 else r[p[1]];b=int(p[-1],0) if op in ('lsli','addi','subi') else r[p[-1]]
            r[p[0]]=((a+b) if op in ('addu','addi') else (a-b) if op in ('subu','subi') else a<<b)&M
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x46d68','--stop-address=0x46e9a',str(wrapper)],text=True))
    layout=json.loads((ROOT/'docs/research/gx8002-imcra-layout-candidate.json').read_text());expected=[(int(row['state_pointer_offset'],0),row['buffer_offset']) for row in layout['arrays']]
    candidate=decode((ROOT/'build/gx8002-backup-imcra-state/state.disassembly.txt').read_text())
    full=execute(code,43008);assert full['success'] and full['writes']==expected,(full,expected)
    assert full['end_offset']==38220
    # Isolate capacity guards by entering after the separate sizing-helper check.
    cases=[]
    capacities={38219,38220,38221,42319,42320,43008}
    for row in layout['arrays']:
        boundary=row['buffer_offset']+row['bytes']
        capacities.update((boundary-1,boundary,boundary+1))
    for capacity in sorted(capacities):
        result=execute(code,capacity);assert result==execute(candidate,capacity,source=True)
        assert result['success']==(capacity>=38220);cases.append({'capacity':capacity,**result})
    report={'stock_sha256':IMAGE_SHA,'compiled_candidate_compared':True,'cases':cases,'observed_end_including_header':38220,'sizing_gate_including_header':42320,'difference':4100,'source_admitted':False,'limits':['Executes allocation block with observed initialized dimensions, after the separate sizing check. Compares compiled candidate and stock pointer stores and success/failure; confirms candidate pointer layout and excess sizing requirement for these defaults, not full initializer or general mutated state behavior.']}
    (ROOT/'docs/research/gx8002-imcra-allocation-trace.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['difference'])

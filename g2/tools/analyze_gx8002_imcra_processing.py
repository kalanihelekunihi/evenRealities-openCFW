# SPDX-License-Identifier: MIT
"""Reachable direct-control-flow inventory, excluding unvisited literal pools."""
import json,subprocess,re
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32

def analyze():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    out=ROOT/'build/gx8002-imcra-processing';out.mkdir(exist_ok=True);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=subprocess.check_output([pre,'-D','--start-address=0x4e674','--stop-address=0x4f200',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True);(out/'stock.disassembly.txt').write_text(raw);code=decode(raw)
    todo=[0x4e674];seen=set();calls={};unresolved=[]
    while todo:
        pc=todo.pop()
        if pc in seen:continue
        assert 0x4e674<=pc<0x4f200,hex(pc)
        op,args,width=code[pc];seen.add(pc)
        if op=='pop' and 'r15' in args or op=='rts':continue
        if op=='bsr':calls.setdefault(int(args,0),[]).append(pc);todo.append(pc+width)
        elif op=='br':todo.append(int(args,0))
        elif op in ('bt','bf','bez','bnez','blz','blsz','bnezad','bhsz','bhz'):
            todo.extend((pc+width,int(args.split(',')[-1].strip(),0)))
        elif op.startswith(('jmp','jsr','bloop','jmpi')):
            unresolved.append({'pc':hex(pc),'op':op,'args':args})
        else:todo.append(pc+width)
    elf=Elf32((ROOT/'build/gx8002-backup-startup-cluster/cluster.elf').read_bytes(),'cluster');targets=[]
    for target,sites in sorted(calls.items()):
        runtime=target+0x10000000-0x38940
        allocated=[s['name'] for s in elf.symbols() if s['value']==runtime and s['type']==2 and s['section'] not in (0,0xfff1)]
        targets.append({'package':hex(target),'runtime':hex(runtime),'sites':[hex(p) for p in sorted(sites)],'source_functions':allocated})
    result={'stock_sha256':IMAGE_SHA,'entry':'0x4e674','reachable_instructions':len(seen),'instruction_bytes':sum(code[p][2] for p in seen),'highest_visited':hex(max(seen)),'direct_targets':targets,'unresolved_control_flow':unresolved,'source_admitted':False,'limits':['Direct control-flow reachability, not function/source reconstruction. No speculative linear-sweep calls from unreachable literal pools. Any unresolved control flow limits inventory completeness.']}
    (ROOT/'docs/research/gx8002-imcra-processing.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(analyze(),indent=2))

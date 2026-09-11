# SPDX-License-Identifier: MIT
"""Conservative local control-flow check for proposed platform-config tail reuse."""
import json
import struct
from analyze_gx8002_clock_table_placement import analyze,ROOT,Elf32,sha
from verify_gx8002_memcpy_source import decode


def analyze_flow():
    placement=analyze()
    elf=Elf32((ROOT/'build/gx8002-board/config.elf').read_bytes(),'config host')
    section=next(s for s in elf.sections if s['name']=='.text.platform_config')
    if sha(elf.contents(section))!=placement['host_compiled_sha256']:raise ValueError('Host ELF identity')
    table=next(s for s in elf.sections if s['name']=='.rodata.platform_config')
    targets=struct.unpack('<10I',elf.contents(table))
    code=decode((ROOT/'build/gx8002-board/config-linked.disassembly.txt').read_text())
    low=section['address'];high=low+section['size'];pending=[low];visited=set()
    while pending:
        pc=pending.pop()
        if pc in visited:continue
        if not low<=pc<high or pc not in code:raise ValueError('Host path leaves compiled text')
        visited.add(pc);op,args,width=code[pc]
        if op=='rts':continue
        if op=='jmp':
            if args!='r3':raise ValueError('Unqualified host indirect branch')
            pending.extend(targets)
        elif op=='br':pending.append(int(args,0))
        elif op in ('bt','bf','bnezad','bez','bnez'):
            pending.extend((pc+width,int(args.split(',')[-1].strip(),0)))
        elif op.startswith('.') or op in ('bsr','jsr','jmpi'):raise ValueError('Unqualified host control flow')
        else:pending.append(pc+width)
    return {'placement':placement,'reachable_instruction_count':len(visited),'dispatch_targets':list(targets),
            'compiled_start':low,'compiled_end':high,'source_admitted':False,
            'limits':['Local host-entry control flow only, assumes existing qualified dispatch bound/table. Does not rule out external entry, arbitrary caller MMIO writes, or startup ownership effects.']}

if __name__=='__main__':
    report=analyze_flow();(ROOT/'docs/research/gx8002-clock-table-host-flow.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Reachable host instructions:',report['reachable_instruction_count'])

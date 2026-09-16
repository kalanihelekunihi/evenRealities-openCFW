# SPDX-License-Identifier: MIT
"""Compare decoded PMU registration against stock and an independent state oracle."""
import itertools, json, re, subprocess
from build_gx8002_backup_pmu_registration import build, ROOT, Elf32, IMAGE_SHA, sha
from verify_gx8002_memcpy_source import decode
M = 0xffffffff
STATE = 0x2002cb88


def execute(code, pc, delta, memory, pointer):
    memory = memory.copy()
    r = {f'r{i}': 0x12340000+i for i in range(32)}
    r['r0'] = pointer
    r['r14'] = 0x20070000
    before = r.copy()
    saved = None
    condition = False
    for _ in range(200):
        op, args, width = code[pc]
        p = [s.strip() for s in args.split(',')]
        nxt = pc + width
        if op == 'push':
            assert args == 'r4, r15'
            saved = r['r4'], r['r15']
            r['r14'] -= 8
        elif op == 'pop':
            assert args == 'r4, r15'
            r['r4'], r['r15'] = saved
            r['r14'] += 8
            assert all(r[f'r{i}'] == before[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'], memory
        elif op in ('lrw', 'movi'): r[p[0]] = int(p[1], 0)
        elif op == 'mov': r[p[0]] = r[p[1]]
        elif op in ('addi','subi'):
            r[p[0]] = (r[p[1] if len(p)==3 else p[0]] + (1 if op=='addi' else -1)*int(p[-1],0)) & M
        elif op == 'addu': r[p[0]] = (r[p[1] if len(p)==3 else p[0]] + r[p[-1]]) & M
        elif op == 'lsli': r[p[0]] = (r[p[1]] << int(p[2],0)) & M
        elif op == 'cmpne': condition = r[p[0]] != r[p[1]]
        elif op == 'cmphsi': condition = r[p[0]] >= int(p[1],0)
        elif op in ('bt','bf','br'):
            if op == 'br' or condition == (op == 'bt'): nxt = int(args,0)
        elif op == 'bez':
            if r[p[0]] == 0: nxt = int(p[1],0)
        elif op == 'bnezad':
            r[p[0]] = (r[p[0]]-1) & M
            if r[p[0]]: nxt = int(p[1],0)
        elif op in ('ld.w','st.w'):
            reg, base, offset = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups()
            address = r[base]+int(offset,0)
            assert address in memory
            if op == 'ld.w': r[reg] = memory[address]
            else: memory[address] = r[reg]
        elif op == 'bsr':
            assert int(args,0)+delta == 0x10011344
            dest, src, length = r['r0'],r['r1'],r['r2']
            assert length == 8
            # The tested inputs are separate or exactly aliased records.
            pair = memory[src], memory[src+4]
            assert dest in memory and dest+4 in memory
            memory[dest], memory[dest+4] = pair
            for i in (0,1,2,3,12,13,15,*range(18,32)): r[f'r{i}'] = 0xbad00000+i
            r['r0'] = dest
        else: raise AssertionError((op,args))
        pc = nxt
    raise AssertionError('execution bound')


def verify():
    build()
    wrapper = ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf = Elf32(wrapper.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data'))) == IMAGE_SHA
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old = decode(subprocess.check_output([pre,'-D','--start-address=0x430c4','--stop-address=0x4319c',str(wrapper)],text=True))
    new = decode((ROOT/'build/gx8002-backup-pmu-registration/callbacks.disassembly.txt').read_text())
    cases = 0
    for resume, count, match, callback, alias in itertools.product((False,True), (0,1,7,8,9,M), range(-1,8), (0,0x10020000,M), range(-1,8)):
        memory = {STATE+i: 0xa0000000+i for i in range(-4,148,4)}
        table = STATE+(80 if resume else 16)
        counter = STATE+(12 if resume else 8)
        memory[counter] = count
        for i in range(8):
            memory[table+i*8] = 0x10030000+i*4
            memory[table+i*8+4] = 0xab000000+i
        if match >= 0: memory[table+match*8] = callback
        pointer = 0x20040000 if alias == -1 else table+alias*8
        memory[pointer],memory[pointer+4] = callback,0xabcdef12
        expected = memory.copy()
        found = next((i for i in range(8) if expected[table+i*8] == callback), None)
        result = 0
        if found is not None: dest = table+found*8
        elif count < 8 and callback:
            dest = table+count*8
            expected[counter] = count+1
        else: dest = None; result = M
        if dest is not None: expected[dest],expected[dest+4] = callback,0xabcdef12
        offset = 0x43130 if resume else 0x430c4
        assert execute(old,offset,0x10000000-0x38940,memory,pointer) == execute(new,offset+0x10000000-0x38940,0,memory,pointer) == (result,expected), (resume,count,match,callback,alias)
        cases += 1
    report = {'cases':cases,'differences':0,'limits':['memcpy is modeled for disjoint or exactly aliased aligned eight-byte records; partial overlaps and concurrent mutations are excluded.', 'Decoded stock/source comparison checks complete modeled memory, return and preserved registers. Hardware and full firmware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-pmu-registration-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__': print(verify())

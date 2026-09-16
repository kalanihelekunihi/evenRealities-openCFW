# SPDX-License-Identifier: MIT
"""Compare decoded PMU initialization against stock and a callback-state oracle."""
import itertools, json, re, subprocess
from build_gx8002_backup_pmu_initialize import build, ROOT, Elf32, IMAGE_SHA, sha
from verify_gx8002_memcpy_source import decode
M = 0xffffffff
STATE = 0x2002cb88


def execute(code, pc, delta, memory, wakeup, mutation):
    memory = memory.copy()
    r = {f'r{i}': 0x12340000+i for i in range(32)}
    trace = []
    r['r14'] = 0x20070000
    before = r.copy()
    saved = None
    condition = False
    for _ in range(200):
        op, args, width = code[pc]
        p = [s.strip() for s in args.split(',')]
        nxt = pc + width
        if op == 'push':
            assert args == 'r4-r6, r15'
            saved = tuple(r[f'r{i}'] for i in (4,5,6,15))
            r['r14'] -= 16
        elif op == 'pop':
            assert args == 'r4-r6, r15'
            r['r4'],r['r5'],r['r6'],r['r15'] = saved
            r['r14'] += 16
            assert all(r[f'r{i}'] == before[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'], memory, trace
        elif op in ('lrw', 'movi'): r[p[0]] = int(p[1], 0)
        elif op == 'mov': r[p[0]] = r[p[1]]
        elif op in ('addi','subi'):
            r[p[0]] = (r[p[1] if len(p)==3 else p[0]] + (1 if op=='addi' else -1)*int(p[-1],0)) & M
        elif op == 'addu': r[p[0]] = (r[p[1] if len(p)==3 else p[0]] + r[p[-1]]) & M
        elif op == 'lsli': r[p[0]] = (r[p[1]] << int(p[2],0)) & M
        elif op == 'cmphs': condition = r[p[0]] >= r[p[1]]
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
        elif op in ('bsr','jsr'):
            target = int(args,0)+delta if op=='bsr' else r[args]
            result = 0xdeadbeef
            if target == 0x10003fb8:
                trace.append(('wakeup',)); result = wakeup
            elif target == 0x100113c4:
                assert (r['r0'],r['r1'],r['r2']) == (STATE,0,144)
                trace.append(('clear',))
                for address in range(STATE,STATE+144,4): memory[address]=0
                result = STATE
            else:
                index = (target-0x10020000)//4
                assert 0 <= index < 8 and target == 0x10020000+index*4
                assert r['r0'] == 0xab000000+index
                trace.append(('resume',index,r['r0']))
                if mutation >= 0: memory[STATE+12] = mutation
            for i in (0,1,2,3,12,13,15,*range(18,32)): r[f'r{i}'] = 0xbad00000+i
            r['r0'] = result
        else: raise AssertionError((op,args))
        pc = nxt
    raise AssertionError('execution bound')


def verify():
    build()
    wrapper = ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf = Elf32(wrapper.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data'))) == IMAGE_SHA
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old = decode(subprocess.check_output([pre,'-D','--start-address=0x43084','--stop-address=0x430c4',str(wrapper)],text=True))
    new = decode((ROOT/'build/gx8002-backup-pmu-initialize/callbacks.disassembly.txt').read_text())
    cases = 0
    for wakeup, count, mutation in itertools.product((0,1,2,3,4,0xffffffff),range(9),(-1,0,1,4,8)):
        memory = {STATE+i: 0xa0000000+i for i in range(-4,148,4)}
        memory[STATE+12] = count
        for i in range(8): memory[STATE+80+i*8],memory[STATE+84+i*8] = 0x10020000+i*4,0xab000000+i
        expected = memory.copy(); trace = [('wakeup',)]
        if wakeup <= 1:
            for address in range(STATE,STATE+144,4): expected[address]=0
            trace.append(('clear',)); result=1
        else:
            index=0; result=0
            while index < expected[STATE+12]:
                trace.append(('resume',index,0xab000000+index))
                if mutation >= 0: expected[STATE+12]=mutation
                index+=1
        assert execute(old,0x43084,0x10000000-0x38940,memory,wakeup,mutation) == execute(new,0x1000a744,0,memory,wakeup,mutation) == (result,expected,trace), (wakeup,count,mutation)
        cases+=1
    report={'cases':cases,'differences':0,'limits':['Wakeup reader, memset and callbacks are modeled. Tests cover valid table counts and callback count mutations within capacity; malformed counts and hardware execution remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-pmu-initialize-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__': print(verify())

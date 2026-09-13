# SPDX-License-Identifier: MIT
"""Execute registered application power dispatch against compiled descriptor data."""
import json, re, struct, subprocess
from build_gx8002_application_descriptor import build, ROOT, sha, Elf32
from verify_gx8002_memcpy_source import decode


def execute(code, entry, memory, seed):
    regs = {f'r{i}': (seed + i * 0x1020304) & 0xffffffff for i in range(32)}
    regs['r14'] = 0x2002f7fc; initial = dict(regs); saved = None; trace = []; pc = entry
    for _ in range(32):
        op, args, width = code[pc]; parts = [p.strip() for p in args.split(',')]; next_pc = pc + width
        if op == 'push':
            assert args == 'r15' and saved is None
            saved = regs['r15']; regs['r14'] -= 4
        elif op in ('lrw', 'movi'): regs[parts[0]] = int(parts[1], 0)
        elif op == 'ld.w':
            match = re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)', args); assert match
            dst, base, offset = match.groups(); address = regs[base] + int(offset, 0)
            regs[dst] = memory[address]; trace.append(['read', address, regs[dst]])
        elif op == 'bez':
            if regs[parts[0]] == 0: next_pc = int(parts[1], 0)
        elif op in ('bsr', 'jsr'):
            assert saved is not None and regs['r14'] == initial['r14'] - 4
            target = int(args, 0) if op == 'bsr' else regs[args]
            trace.append(['call', target, [] if op == 'bsr' else [regs['r0']]])
            for i in (0, 1, 2, 3, 12, 13, 15, *range(18, 32)):
                regs[f'r{i}'] = (seed ^ 0xcafe0000 ^ i) & 0xffffffff
        elif op == 'pop':
            assert args == 'r15' and saved is not None
            regs['r15'] = saved; regs['r14'] += 4
            assert all(regs[f'r{i}'] == initial[f'r{i}'] for i in (*range(4, 12), 14, 15, 16, 17))
            return regs['r0'], trace
        else: raise AssertionError((pc, op, args))
        pc = next_pc
    raise AssertionError('execution bound')


def verify():
    candidate = build(); base = 0x20026d38
    path = ROOT / 'build/gx8002-application-descriptor/descriptor.elf'; elf = Elf32(path.read_bytes(), 'descriptor')
    memory = {}
    for section in elf.sections:
        if not section['flags'] & 2 or not section['size']: continue
        body = elf.contents(section)
        for offset in range(0, len(body), 4): memory[section['address'] + offset] = struct.unpack_from('<I', body, offset)[0]
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'); cases = 0; hashes = {}
    for kind, field in (('suspend', 16), ('resume', 24)):
        path = ROOT / 'build/gx8002-source-candidate' / kind / 'setter.elf'; elf = Elf32(path.read_bytes(), kind)
        report = json.loads((ROOT / 'docs/research' / ('gx8002-app-' + kind + '-verification.json')).read_text())
        section = next(s for s in elf.sections if s['name'] == '.text.' + report['symbol'])
        assert sha(elf.contents(section)) == report['compiled_sha256']; hashes[kind] = sha(path.read_bytes())
        code = decode(subprocess.check_output([pre, '-d', str(path)], text=True))
        for seed in (0, 91, 0xffffffff):
            for variant in ('compiled', 'null_app', 'null_callback'):
                data = dict(memory); descriptor = data[base]
                if variant == 'null_app': data[base] = 0
                if variant == 'null_callback': data[descriptor + field] = 0
                expected = [['call', 0x102067ac, []]] if kind == 'suspend' else []
                expected.append(['read', base, data[base]])
                if data[base]:
                    target = data[descriptor + field]; expected.append(['read', descriptor + field, target])
                    if target:
                        context = data[descriptor + field + 4]
                        expected += [['read', descriptor + field + 4, context], ['call', target, [context]]]
                assert execute(code, section['address'], data, seed) == (0, expected)
                cases += 1
    return {'candidate': candidate, 'dispatcher_elf_sha256': hashes, 'cases': cases,
            'source_admitted': False, 'hardware_qualified': False,
            'limits': ['Registered suspend/resume instructions dispatch compiled descriptor targets and matching private strings. Null object/callback branches and callee-saved registers checked.',
                       'Watchdog and callback bodies are returning models with caller-register clobbers. Callback definitions still require SDK type reconciliation; no physical power-transition qualification.']}


if __name__ == '__main__':
    result = verify(); assert json.loads(json.dumps(result)) == result
    (ROOT / 'docs/research/gx8002-application-descriptor-power-dispatch.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Application power descriptor dispatch:', result['cases'], 'cases')

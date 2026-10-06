#!/usr/bin/env python3
"""Execute stock/public-HAL interrupt-clear leaf against synthetic MSPI pages."""
import argparse
import importlib.util
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('bootv', ROOT / 'g2/components/bootloader/update_core/verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.ENTRIES['mspi_interrupt_clear'] = 0x426506
HANDLE = 0x20032000
MSPI = 0x40060000

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--elf', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases, trace = [], {}
    for magic, module, mask in itertools.product([0, 0x01bebebe, 0xfdbebebe, 0xffffffff], range(3), [0, 1, 0xffffffff]):
        pair = [v.Machine(), v.Machine(True, segments, symbols)]
        results = []
        for m in pair:
            m.cpu.mem_map(MSPI, 0x3000)
            m.w(HANDLE, magic)
            m.w(HANDLE + 4, module)
            m.w(MSPI + module * 0x1000 + 0x204, 0x12345678)
            d = m.run('mspi_interrupt_clear', [HANDLE, mask])
            d['register_page_sha256'] = v.hashlib.sha256(m.cpu.mem_read(MSPI, 0x3000)).hexdigest()
            expected = 0 if (magic & 0x01ffffff) == 0x01bebebe else 2
            assert d['return'] == expected
            assert m.u(MSPI + module * 0x1000 + 0x208) == (mask if expected == 0 else 0)
            results.append(d)
        assert results[0] == results[1]
        trace.update(pair[0].trace)
        cases.append(dict(magic=magic, module=module, mask=mask, result=results[0]))
    pair = [v.Machine(), v.Machine(True, segments, symbols)]
    results = [m.run('mspi_interrupt_clear', [0, 0xffffffff]) for m in pair]
    assert results[0] == results[1] and results[0]['return'] == 2
    trace.update(pair[0].trace)
    cases.append(dict(handle=0, result=results[0]))
    used = {int(pc, 0) + i for pc, raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
    upstream = ROOT / 'g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510'
    sources = [p for p in Path(__file__).parent.iterdir() if p.is_file()] + [p for p in upstream.rglob('*') if p.is_file() and p.suffix in ['.c', '.h']]
    d = dict(status='PASS', cases=len(cases), comparisons=cases, original_trace=trace,
             distinct_original_trace_bytes=len(used), original_sha256=v.SHA,
             elf_sha256=v.sha(args.elf), source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in sources},
             limits=['Real original and pinned public HAL leaf instructions execute; no returning provider stubs in this leaf.',
                     'Synthetic register memory preserves seeded INTSTAT; no interrupt clearing semantics, clock timing or peripheral bus effects are modeled.',
                     'Stock disassembly includes INTSTAT read after INTCLR write; tests validate return and complete synthetic page state, not hardware read side effects.',
                     'Only modules 0..2 and valid mapped handles tested; no added range guard or malformed-pointer safety claim.',
                     'This validates one leaf, not full MSPI, flash driver, bootability or byte-identical build.'])
    args.output.write_text(json.dumps(d, indent=2) + '\n')
    print(json.dumps({k:d[k] for k in ['status','cases','distinct_original_trace_bytes']}))

if __name__ == '__main__':
    main()

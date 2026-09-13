# SPDX-License-Identifier: MIT
"""Compose current-layout initialization, IRQ registration and DMA delivery."""
import json
from itertools import product
from build_gx8002_backup_dma_initialize import build as initialize_build, ROOT
from build_gx8002_backup_request_irq import build as request_build
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_dma_initialize import execute as initialize
from verify_gx8002_backup_request_irq import execute as register
from verify_gx8002_backup_dma_irq_registration import dispatch
from verify_gx8002_backup_dma_irq import execute as dma
import subprocess


def authenticated_code(kind, artifact, baseline):
    path = ROOT/'build/gx8002-source-candidate'/kind/artifact
    elf = Elf32(path.read_bytes(), str(path))
    report = json.loads((ROOT/'docs/research'/baseline).read_text())
    assert report['source_admitted']
    for row in report['functions']:
        section = next(s for s in elf.sections if s['name'] == row['section_name'])
        assert sha(elf.contents(section)) == row['compiled_sha256']
        assert section['size'] == row['compiled_bytes']
        assert not elf.relocations(section['index'])
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    return decode(subprocess.check_output([pre, '-d', str(path)], text=True)), sha(path.read_bytes())


def verify():
    builds = {'initialize': initialize_build(), 'register': request_build()}
    init = decode((ROOT/'build/gx8002-backup-dma-initialize/initialize.disassembly.txt').read_text())
    reg = decode((ROOT/'build/gx8002-backup-request-irq/request.disassembly.txt').read_text())
    irq, irq_sha = authenticated_code('backup-irq-entry', 'entry.elf', 'gx8002-backup-irq-entry-source-verification.json')
    handler, handler_sha = authenticated_code('backup-dma-shared', 'pair.elf', 'gx8002-backup-dma-shared-source-verification.json')
    # Existing body interpreter uses package PCs. Rebase the current compiled
    # body's PCs and local branch only; table and peripheral addresses stay real.
    body = {}
    delta = 0x3d1c0 - 0x10004880
    for pc, (op, args, width) in irq.items():
        if not 0x10004892 <= pc < 0x100048b0:
            continue
        if op == 'bez':
            register_name, target = args.split(',')
            assert int(target.strip(), 0) == 0x100048b0
            args = register_name + ', ' + hex(int(target.strip(), 0) + delta)
        body[pc + delta] = (op, args, width)
    cases = deliveries = 0
    for seed, base, status in product((0, 0xffffffff, 0x12345678), (0xa1000000, 0xa1001000), (0, 1, 0xffffffff)):
        writes = []
        def hook(number, target, context):
            writes.extend(register(reg, 0x10004844, number, target, context))
        initialize(init, 0x10004d14, seed, base, status, state=0x2002d3e8,
                   gate=0x10003be8, request_irq=0x10004844, irq_hook=hook)
        assert writes == [(0x200173f8, 0x10004c04), (0x200173fc, 0), (0xe000e100, 1024)]
        memory = dict(writes)
        for active in (42, 0xfffffe2a):
            calls = dispatch(body, memory, active)
            assert calls == [(0x10004c04, 10, 0)]
            for pending, callbacks in product((0, 1, 2, 3, 4, 0x80000000, 0xffffffff),
                                             ((0, 0), (0x10004054, 0), (0, 0x10004034), (0x10004054, 0x10004034))):
                result, trace, _ = dma(handler, calls[0][0], pending, callbacks, False, status,
                                       helper_addresses={0x10004bc0: 0x10203a98})
                wanted = [('callback', cb, private) for ch, (cb, private) in
                          enumerate(zip(callbacks, (0x1234, 0x5678))) if pending & (1 << ch) and cb]
                assert result == 0
                assert [row for row in trace if row[0] == 'callback'] == wanted
                assert [row for row in trace if row[0] == 'deallocate'] == [('deallocate', ch) for ch in range(2) if pending & (1 << ch)]
                deliveries += 1
            cases += 1
        memory[0x200173f8] = 0
        assert dispatch(body, memory, 42) == []
        cases += 1
    report = {'builds': builds, 'source_irq_elf_sha256': irq_sha,
              'source_dma_elf_sha256': handler_sha, 'registration_dispatch_cases': cases,
              'dma_delivery_cases': deliveries, 'handler_runtime_address': 0x10004c04,
              'source_admitted': False, 'hardware_qualified': False,
              'limits': ['Current source artifacts authenticated against reviewed admission reports.',
                         'Resource helper, deallocator and final callback bodies are modeled.',
                         'Dispatcher body only here; full architecture context is qualified separately.',
                         'Synthetic pending interrupts; no physical IRQ delivery or device timing qualification.']}
    (ROOT/'docs/research/gx8002-backup-dma-current-registration.json').write_text(json.dumps(report, indent=2)+'\n')
    return report

if __name__ == '__main__':
    r = verify()
    print(r['registration_dispatch_cases'], 'registration cases;', r['dma_delivery_cases'], 'DMA delivery cases')

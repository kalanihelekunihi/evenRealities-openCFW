# SPDX-License-Identifier: MIT
"""Rebuild and qualify the exact linked backup UART cluster on macOS."""
import json
import subprocess
from itertools import product
from build_gx8002_backup_uart_interrupt import build, ROOT, sha
from verify_gx8002_backup_uart_interrupt_buffered import verify as buffered
from verify_gx8002_backup_uart_interrupt_mutation import verify as mutation
from verify_gx8002_backup_uart_interrupt_stall import verify as stall
from verify_gx8002_backup_uart_interrupt_counts import verify as counts
from verify_gx8002_uart_fifo_depth import execute as execute_fifo
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_double_wrapper_references import analyze
from analyze_gx8002_backup_uart_references import verify as resolve_references


def verify():
    candidate = build()
    assert candidate['fits'] and not candidate['dispatch_differences']
    path = ROOT / 'build/gx8002-backup-uart-interrupt/interrupt.elf'
    identity = candidate['elf_sha256']
    results = {}
    for name, run in [('buffered', buffered), ('mutation', mutation), ('stall', stall), ('counts', counts)]:
        result = run()
        tested = result.get('source_elf_sha256') or result['candidate']['elf_sha256']
        assert tested == identity
        assert sha(path.read_bytes()) == identity
        results[name] = result
    tool = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code = decode(subprocess.check_output([tool, '-d', str(path)], text=True))
    fifo_cases = 0
    for encoding, other, port in product(range(256), (0, 0xff00ffff, 0xa5001234), (0, 1)):
        device = 0xa0100000 + port * 0x100000
        descriptor = 0x20016b84 + port * 128
        parameter = encoding << 16 | other
        depth = encoding << 4 if encoding and not encoding & (encoding - 1) else 0
        assert execute_fifo(code, 0x1000433c, device, parameter, descriptor) == (depth, [(descriptor + 4, device), (device + 0xf4, parameter)])
        fifo_cases += 1
    references = analyze(0x3cc7c, 0x3cce4)
    assert all(row['entry'] for row in references['external_branches'])
    assert not references['external_literal_pools'] and not references['stored_address_words']
    resolved = resolve_references()
    assert resolved['bounded_interrupt_reference_candidates_resolved']
    assert not resolved['interrupt']['external_branches']
    assert all(row['entry'] for row in resolved['interrupt']['stored_address_words'])
    return {'resolved_reference_evidence':resolved,'elf_sha256': identity, 'candidate': candidate, 'interrupt_results': results, 'linked_fifo_cases': fifo_cases, 'total_cases': candidate['dispatch_cases'] + sum(r['cases'] for r in results.values()) + fifo_cases, 'fifo_envelope_references': references, 'source_admitted': False, 'hardware_qualified': False, 'limits': ['All behavioral reports are generated for and bound to the same complete linked ELF. FIFO exercised directly from that ELF. Reference census is bounded, excludes computed control flow and does not prove full firmware integration. The two apparent interrupt interior references are resolved as literal-word misdecoding by the included authenticated analysis; arbitrary computed flow remains outside scope.']}


if __name__ == '__main__':
    result = verify()
    (ROOT / 'docs/research/gx8002-backup-uart-cluster.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Linked cluster cases:', result['total_cases'], result['elf_sha256'])

# SPDX-License-Identifier: MIT
"""Resolve UART census candidates against the current source composition."""
import json
import subprocess
from analyze_gx8002_double_wrapper_references import analyze
from verify_gx8002_memcpy_source import decode
from build_gx8002_backup_cfft import ROOT, IMAGE, IMAGE_SHA, sha, Elf32


def verify():
    directory = ROOT / 'build/gx8002-fft-q15-uart-integration-experiment'
    report = json.loads((directory / 'build-report.json').read_text())
    firmware = (directory / 'firmware_codec.unadmitted.bin').read_bytes()
    assert sha(firmware) == report['firmware_sha256']
    interrupt = analyze(0x3cb90, 0x3cc7c, False)
    fifo = analyze(0x3cc7c, 0x3cce4, False)
    path = ROOT / 'build/gx8002-backup-clock-frequency/frequency.elf'
    elf = Elf32(path.read_bytes(), 'source frequency')
    section = next(s for s in elf.sections if s['name'] == '.text')
    start = section['address'] - 0x10003000 + 0x3b940
    body = elf.contents(section)
    assert start == 0x3c630 and len(body) == 468
    assert firmware[start:start + len(body)] == body
    pools = interrupt['external_literal_pools']
    assert pools == [{'pc': 0x3c812, 'pool': 0x3cbd0}, {'pc': 0x3c81a, 'pool': 0x3cbe4}]
    # Decode bounded real reader sites, not the literal words as instructions.
    tail = analyze(0x3c808, 0x3c81c, False)
    readers = [(0x3c726, 0x3c808, 0xa0005000),
               (0x3c780, 0x3c80c, 0xfff83000),
               (0x3c786, 0x3c810, 0x000f9fff),
               (0x3c78e, 0x3c814, 0xfffda800),
               (0x3c792, 0x3c818, 0x002c87ff)]
    assert tail['external_literal_pools'] == [dict(pc=pc, pool=pool) for pc, pool, value in readers]
    assert not tail['external_branches'] and not tail['stored_address_words']
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    wrapper = ROOT/'build/gx8002-board/padmux-get-stock.elf'
    objdump = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    for pc, pool, value in readers:
        code = decode(subprocess.check_output([objdump, '-D', f'--start-address={pc:#x}', f'--stop-address={pc+2:#x}', str(wrapper)], text=True))
        op, args, width = code[pc]
        assert op == 'lrw' and width == 2 and int(args.split(',')[-1], 0) == value
        assert int.from_bytes(stock[pool:pool+4], 'little') == value
        assert start <= pc < start + len(body)
    candidates = []
    for candidate in pools:
        row = next(r for r in report['ownership'] if r['offset'] <= candidate['pc'] < r['offset'] + r['size'])
        assert row == {'offset': 0x3c804, 'size': 24, 'kind': 'retained_stock'}
        candidates.append({**candidate, 'containing_region': row, 'outside_complete_source_frequency_body': True, 'stock_literal_word': next({'reader':pc,'pool':pool,'value':value} for pc,pool,value in readers if pool <= candidate['pc'] < pool+4), 'classification':'linear decoding of the upper half of a verified stock literal word'})
    return {'stock_sha256': IMAGE_SHA, 'firmware_sha256': sha(firmware), 'frequency_elf_sha256': sha(path.read_bytes()), 'frequency_body_matches_composed_source': True, 'interrupt': interrupt, 'fifo': fifo, 'interior_pool_candidates': candidates, 'frequency_literal_tail_census':tail, 'bounded_interrupt_reference_candidates_resolved':True, 'source_admitted': False, 'limits': ['Both apparent UART interior references decode upper halves of verified frequency literal words. All five bounded literal consumers lie in the replaced source frequency body; the tail census finds no branch or stored pointer into that data. This resolves these candidates within the bounded census, not arbitrary computed control flow. Tail bytes are not reclaimed by this analysis.']}


if __name__ == '__main__':
    result = verify()
    (ROOT / 'docs/research/gx8002-backup-uart-references.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Authenticated frequency body; interior pool candidates:', len(result['interior_pool_candidates']))

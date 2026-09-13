# SPDX-License-Identifier: MIT
"""Check source backup release wrapper and nested compiled deallocation."""
import json, subprocess
from itertools import product
from build_gx8002_backup_dma_release import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_dma_release import execute as wrapper
from verify_gx8002_backup_dma_deallocate import execute as deallocate
from verify_gx8002_backup_dma_current_registration import authenticated_code


def verify():
    candidate = build()
    stock = IMAGE.read_bytes(); assert sha(stock) == IMAGE_SHA
    path = ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf = Elf32(path.read_bytes(), str(path))
    assert elf.contents(next(s for s in elf.sections if s['name'] == '.data')) == stock
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old = decode(subprocess.check_output([pre, '-D', '--start-address=0x3d5bc', '--stop-address=0x3d5c4', str(path)], text=True))
    new = decode((ROOT/'build/gx8002-backup-dma-release/release.disassembly.txt').read_text())
    shared, shared_sha = authenticated_code('backup-dma-shared', 'pair.elf', 'gx8002-backup-dma-shared-source-verification.json')
    mapping = {0x1000486c:0x10025560, 0x10004878:0x1002556c, 0x10003be8:0x10025080}
    cases = 0; state = 0x2002d3e8
    for flags, channel, token in product(product((0,1,2,255), repeat=2), range(2), (0,0x40,0xffffffff)):
        def hook(ch):
            assert ch == channel
            return deallocate(shared, 0x10004bc0, flags, token, ch, helper_addresses=mapping, count=2)
        a = wrapper(old, 0x3d5bc, channel, hook, deallocate_address=0x3d500)
        b = wrapper(new, 0x10004c7c, channel, hook, deallocate_address=0x10004bc0)
        assert a == b
        trace, memory = b
        remaining = list(flags); remaining[channel] = 0
        assert memory == {state+4:2, **{state+0x370+i:v for i,v in enumerate(remaining)}}
        assert trace[0] == ('irq_save',) and trace[-1] == ('irq_restore',token)
        assert [r for r in trace if r[0]=='resource'] == ([] if 1 in remaining else [('resource',25,0)])
        cases += 1
    return {'candidate':candidate, 'shared_elf_sha256':shared_sha, 'decoded_composition_cases':cases,
            'source_admitted':False, 'hardware_qualified':False,
            'limits':['Exact three-instruction wrapper and compiled deallocator composed at call boundary.',
                      'Original wrapper frame retained; IRQ/resource helpers modeled, physical concurrency unqualified.']}

if __name__ == '__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-release-verification.json').write_text(json.dumps(r,indent=2)+'\n')
    print(r['decoded_composition_cases'], 'release composition cases passed')

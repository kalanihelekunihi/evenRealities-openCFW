# SPDX-License-Identifier: MIT
"""Compose compiled backup abort with the admitted shared deallocator."""
import json
from itertools import product
from verify_gx8002_backup_dma_current_registration import authenticated_code, ROOT
from verify_gx8002_backup_dma_abort import execute as abort
from verify_gx8002_backup_dma_deallocate import execute as deallocate


def verify():
    code, abort_sha = authenticated_code('backup-dma-abort', 'abort.elf', 'gx8002-backup-dma-abort-source-verification.json')
    shared, shared_sha = authenticated_code('backup-dma-shared', 'pair.elf', 'gx8002-backup-dma-shared-source-verification.json')
    mapping = {0x1000486c: 0x10025560, 0x10004878: 0x1002556c, 0x10003be8: 0x10025080}
    state = 0x2002d3e8
    cases = 0
    for flags, channel, base, token, status in product(product((0, 1, 2, 255), repeat=2),
                                                     range(2), (0xa1000000, 0xa1001000),
                                                     (0, 0x98765432), (0, 1, 0xffffffff)):
        invoked = []
        def hook(ch):
            invoked.append((ch, deallocate(shared, 0x10004bc0, flags, token, ch,
                                           helper_addresses=mapping, count=2)))
        result, trace = abort(code, 0x10004c84, channel, base, status, deallocate_hook=hook)
        expected = [('read', state, base), ('write', base + 0x3a0, 256 << channel)]
        expected += [('write', base + off, 1 << channel) for off in (0x338, 0x340, 0x348, 0x350, 0x358)]
        expected += [('deallocate', channel)]
        assert result == 0 and trace == expected
        assert len(invoked) == 1 and invoked[0][0] == channel
        inner, memory = invoked[0][1]
        remaining = list(flags)
        remaining[channel] = 0
        assert memory == {state+4: 2, **{state+0x370+i: v for i, v in enumerate(remaining)}}
        assert inner[0] == ('irq_save',) and inner[-1] == ('irq_restore', token)
        assert [r for r in inner if r[0] == 'resource'] == ([] if 1 in remaining else [('resource', 25, 0)])
        cases += 1
    report = {'abort_elf_sha256': abort_sha, 'shared_elf_sha256': shared_sha,
              'decoded_composition_cases': cases, 'source_admitted': False,
              'hardware_qualified': False,
              'limits': ['Actual compiled abort and deallocator composed at the helper boundary.',
                         'Two initialized channels; flags unequal to one are inactive, matching stock.',
                         'IRQ save/restore and resource gate remain modeled; hardware timing remains unqualified.']}
    (ROOT/'docs/research/gx8002-backup-dma-abort-deallocation.json').write_text(json.dumps(report, indent=2)+'\n')
    return report

if __name__ == '__main__':
    print(verify()['decoded_composition_cases'], 'abort/deallocation cases passed')

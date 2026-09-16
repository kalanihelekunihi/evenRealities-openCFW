# SPDX-License-Identifier: MIT
"""Qualify signed loop limits separately from unsigned cursor accounting."""
import json
import subprocess
from itertools import product
from build_gx8002_backup_uart_interrupt import build, ROOT, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_interrupt import execute


def verify():
    candidate = build()
    out = ROOT / 'build/gx8002-backup-uart-interrupt'
    wrapper = ROOT / 'build/gx8002-board/padmux-get-stock.elf'
    stock = Elf32(wrapper.read_bytes(), 'stock')
    assert sha(stock.contents(next(s for s in stock.sections if s['name'] == '.data'))) == IMAGE_SHA
    objdump = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old = decode(subprocess.check_output([objdump, '-D', '--start-address=0x3cb90', '--stop-address=0x3cc7c', str(wrapper)], text=True))
    new = decode(subprocess.check_output([objdump, '-d', str(out / 'interrupt.elf')], text=True))
    cases = 0
    for pending, length, available in product((2, 4), (0, 1, 4, 0x7fffffff, 0x80000000, 0x80000001, 0xffffffff), (0, 1, 4, 0x7fffffff, 0x80000000, 0xffffffff)):
        count = min(length, available)
        # Huge positive transfers require corresponding real buffers; do not
        # turn a verifier bound into a claim about those executions.
        if 4 < count < 0x80000000:
            continue
        base, device, buffer = 0x20016b84, 0xa0100000, 0x20060000
        d = [0] * 32
        d[1] = device
        d[16] = d[17] = 2
        d[24] = d[29] = buffer
        d[25] = d[30] = length
        d[22], d[27] = 0x10300020, 0x10300030
        regs = {device + off: 0 for off in range(0, 256, 4)}
        regs.update({buffer + off: 0x76543210 for off in range(0, 16, 4)})
        regs.update({device: 0xab, device + 4: 3, device + 8: pending, device + 20: 64, device + 0x84: available, device + 0x80: (16 - available) & 0xffffffff, device + 0xf4: 1 << 16})
        a = execute(old, 0x3cb90, d, regs, descriptor_base=base)
        b = execute(new, 0x10004250, d, regs, descriptor_base=base)
        assert a == b, (pending, length, available, a[2], b[2])
        result, memory, trace = b
        cursor_index, length_index = (24, 25) if pending == 4 else (29, 30)
        assert result == 0
        assert memory[base + cursor_index * 4] == (buffer + count) & 0xffffffff
        assert memory[base + length_index * 4] == length - count
        transfers = count if count < 0x80000000 else 0
        received = [x for x in trace if x[0] == 'write' and x[2] == 1]
        sent = [x for x in trace if x[0] == 'write' and x[1] == device]
        assert len(received) == (transfers if pending == 4 else 0)
        assert len(sent) == (transfers if pending == 2 else 0)
        callbacks = [x for x in trace if x[0] == 'callback']
        assert len(callbacks) == int(count == length)
        cases += 1
    return {'source_elf_sha256': candidate['elf_sha256'], 'stock_sha256': IMAGE_SHA, 'cases': cases, 'source_admitted': False, 'limits': ['Tests zero, small positive and sign-bit-set counts, including unsigned transmit availability underflow. Large positive transfers excluded. Preserves stock signed-loop behavior; does not establish that malformed descriptor lengths are safe. MMIO and callbacks modeled; no hardware execution.']}


if __name__ == '__main__':
    result = verify()
    (ROOT / 'docs/research/gx8002-backup-uart-interrupt-counts.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Count boundary cases:', result['cases'])

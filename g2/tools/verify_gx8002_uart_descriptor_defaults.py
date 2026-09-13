# SPDX-License-Identifier: MIT
"""Bounded decoded check of unnamed UART defaults and line-control behavior."""
import json
import subprocess
from itertools import product
from pathlib import Path
from analyze_gx8002_upstream_objects import IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_configure import arithmetic
from execute_gx8002_uart_configure import execute

ROOT = Path(__file__).resolve().parents[1]


def verify():
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    stock_path = ROOT / 'build/gx8002-board/padmux-get-stock.elf'
    stock_elf = Elf32(stock_path.read_bytes(), 'stock')
    assert sha(stock_elf.contents(next(s for s in stock_elf.sections if s['name'] == '.data'))) == IMAGE_SHA
    stock = decode(subprocess.check_output([pre+'objdump', '-D', '--start-address=0xc8ec', '--stop-address=0x17574', str(stock_path)], text=True))
    source_path = ROOT / 'build/gx8002-uart-configure-source/configure.elf'
    report = json.loads((ROOT / 'docs/research/gx8002-uart-configure-source-verification.json').read_text())
    source_elf = Elf32(source_path.read_bytes(), 'source')
    section = next(s for s in source_elf.sections if s['name'] == '.text')
    assert sha(source_elf.contents(section)) == report['functions'][0]['compiled_sha256']
    source = decode(subprocess.check_output([pre+'objdump', '-d', str(source_path)], text=True))
    bindings = report['bindings']
    names = dict(uint='__floatunsidf', divide='__divdf3', multiply='__muldf3', add='__adddf3', fix='__fixunsdfsi', fifo='open_cfw_gx8002_uart_fifo_depth', irq='open_cfw_gx8002_request_irq')
    source_helpers = {bindings[name]: kind for kind, name in names.items()}
    stock_symbols = dict(uint=0x13a5c, divide=0x13894, multiply=0x13694, add=0x13628, fix=0x12ff8, pack=0x13b00, unpack=0x13c90, integer=0x13ab4, core=0x13364, compare=0x139ac, compare_parts=0x13d74, signed=0x139ec, subtract=0x13658, fifo=0xc8ec, irq=0xffe2eac8)
    stock_helpers = {stock_symbols[k]: k for k in names}
    # Both configurations call the already decoded stock arithmetic in isolated
    # frames. This test focuses on descriptor fields, not arithmetic composition.
    numeric = arithmetic(stock, stock_symbols)
    cases = 0
    for port, baud, mode, control in product((0, 1), (0, 115200), (0, 1), (0, 0xffffffff)):
        base = 0x20026a94 + port * 128
        device = (0xa0100000, 0xa0200000)[port]
        regs = {device+off: 0 for off in range(0, 0x100, 4)}
        regs[device+12] = control
        baseline = None
        for field7, field8 in product((0, 1, 7, 8, 9, 0xffffffff), (0, 1, 2, 3, 0xffffffff)):
            descriptor = [0]*32
            descriptor[0] = port
            descriptor[1] = device
            descriptor[3] = 24000000
            descriptor[4] = baud
            descriptor[7] = field7
            descriptor[8] = field8
            descriptor[9] = mode
            descriptor[15] = 6+port
            a = execute(stock, 0xc954, descriptor, regs, stock_helpers, numeric, 16, descriptor_base=base)
            b = execute(source, 0x102033c8, descriptor, regs, source_helpers, numeric, 16, descriptor_base=base)
            assert a == b, ('decoded mismatch', cases)
            result, memory, trace = a
            assert result == 0
            assert memory[base+28] == (field7 or 8)
            assert memory[base+32] == (field8 or 1)
            assert memory[device+12] == ((control & ~31) | 3)
            # Remove only the two variable descriptor words and their accesses.
            # Every other read, write, helper argument and final word must agree.
            excluded = {base+28, base+32}
            invariant = ({k:v for k,v in memory.items() if k not in excluded},
                         [t for t in trace if not (t[0] in ('read','write') and t[1] in excluded)])
            if baseline is None:
                baseline = invariant
            assert invariant == baseline, ('field affects other state', cases)
            cases += 1
    return {'cases': cases, 'stock_sha256': IMAGE_SHA, 'source_elf_sha256': sha(source_path.read_bytes()),
            'evidence_sha256': {n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_uart_descriptor_defaults.py', 'execute_gx8002_uart_configure.py', 'verify_gx8002_uart_configure.py', 'verify_gx8002_memcpy_source.py')},
            'source_admitted': False, 'hardware_qualified': False,
            'findings': ['In this decoded configuration corpus, words 7 and 8 are normalized from zero to 8 and 1 respectively; nonzero values are retained.', 'Varying these words changes no other observed state or helper/MMIO trace. Line control always clears bits 0..4 and sets value 3.'],
            'limits': ['This tests the configuration function, not every descriptor consumer. It does not establish original field names or whole-program non-use.', 'FIFO and IRQ helpers are modeled; arithmetic executes decoded stock helper bodies. No physical peripheral execution.']}

if __name__ == '__main__':
    result = verify()
    (ROOT/'docs/research/gx8002-uart-descriptor-defaults.json').write_text(json.dumps(result, indent=2)+'\n')
    print('UART descriptor default cases:', result['cases'])

#!/usr/bin/env python3
"""Pin corrected runtime PC and module-13 clock branch against SDK source."""
from pathlib import Path
import hashlib, json, re, subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
STOCK = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage1.bin'
OBJDUMP = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump'
SDK = ROOT / 'third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/include/clk_priv.h'
raw = STOCK.read_bytes()
listing = subprocess.check_output([str(OBJDUMP), '-D', '-b', 'binary', '-m', 'csky', '--no-show-raw-insn', '--adjust-vma=0x0fffffe8', '--start-address=0x100001f8', '--stop-address=0x10000300', str(STOCK)], text=True)
assert '100001f8:' in listing and '10000206:' in listing and '0x10001324' in listing
assert '10000260:' in listing and '100002d4:' in listing

def words(vma, count):
    off = vma - 0x0fffffe8
    return [int.from_bytes(raw[off+i*4:off+i*4+4], 'little') for i in range(count)]

high = words(0x10001324, 18)
all_gate = words(0x1000136c, 19)
assert high[13-7] == 0x100002b4
assert all_gate[13-6] == 0x100002d4
source = SDK.read_text()
assert re.search(r'case CLOCK_MODULE_FLASH_SPI:\s*gate \|= 1 << 13;', source)
assert '_clk_set_high_gate' in source and '_clk_set_all_gate' in source
r = {'stock_sha256': hashlib.sha256(raw).hexdigest(), 'runtime_address_rule': 'file offset + 0x0fffffe8',
     'clock_dispatch_entry': '0x100001f8', 'module_13_high_branch': hex(high[6]),
     'module_13_all_branch': hex(all_gate[7]), 'pinned_sdk_sha256': hashlib.sha256(SDK.read_bytes()).hexdigest(),
     'module_13_static_branch_proven': True, 'full_mmio_effects_proven': False}
(HERE/'clock-gate-native-dispatch-receipt.json').write_text(json.dumps(r, indent=2)+'\n')
print('clock module13 native dispatch PASS')

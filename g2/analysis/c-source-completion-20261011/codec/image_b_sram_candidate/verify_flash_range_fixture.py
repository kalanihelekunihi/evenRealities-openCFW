#!/usr/bin/env python3
"""Check the eleven stock/source flash-range traces from a QEMU fixture.

The paired ELF is built with process_native_oracle_stock.S and the selected
profile-leaf C source. It is a test artifact, not firmware source or flash
hardware proof.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
ELF = HERE / "flash-range-oracle.elf"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_flash_callback_profile_leaves.c"

command = ["docker", "run", "--rm", "--network=none", "-v", f"{ROOT}:/repo",
           "-w", "/repo", "opencfw/qemu-csky-builddeps:20261009t201800",
           "sh", "-lc", "timeout 15s /repo/g2/build/offline-xuantie-csky-dsp-20261009T201800Z/qemu-system-cskyv2 "
           "-M virt -m 1G -cpu ck804ef -nographic -monitor none "
           f"-kernel /repo/{ELF.relative_to(ROOT)} -d guest_errors -D /tmp/flash-range.log; "
           "cat /tmp/flash-range.log"]
run = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
log = run.stdout + run.stderr
words = [int(x) & 0xffffffff for x in re.findall(r"label: (-?\d+)", log)]
rows = [words[i:i+5] for i in range(0, len(words), 5)]
passed = (len(rows) == 11 and all(len(r) == 5 and r[0] == i and
          r[1] == r[3] and r[2] == r[4] for i, r in enumerate(rows)) and
          "csky_exit_write: exit(0)" in log)
receipt = {
    "result": "PASS" if passed else "FAIL", "cases": len(rows),
    "native_and_source_words_per_case": 4, "rows": rows,
    "elf_sha256": hashlib.sha256(ELF.read_bytes()).hexdigest(),
    "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "scope": "CK804EF QEMU paired original-byte/C 0x100075d0 range mapper; eleven descriptor/address/length cases including zero and wrap",
    "limits": ["Does not exercise physical flash", "Does not qualify other callbacks"],
}
out = HERE / "flash-range-oracle-receipt.json"
out.write_text(json.dumps(receipt, indent=2) + "\n")
print(out)
print(receipt["result"], len(rows))
if not passed:
    raise SystemExit(1)

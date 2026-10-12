#!/usr/bin/env python3
"""Bounded original-byte/C audio dB return and state check on CK804EF QEMU."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
ELF = HERE / "audio-db-oracle.elf"
cmd = ["docker", "run", "--rm", "--network=none", "-v", f"{ROOT}:/repo",
       "-w", "/repo", "opencfw/qemu-csky-builddeps:20261009t201800",
       "sh", "-lc",
       "timeout 15s /repo/g2/build/offline-xuantie-csky-dsp-20261009T201800Z/qemu-system-cskyv2 "
       "-M virt -m 1G -cpu ck804ef -nographic -monitor none "
       f"-kernel /repo/{ELF.relative_to(ROOT)} -d guest_errors -D /tmp/audio-db.log; "
       "cat /tmp/audio-db.log"]
run = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
log = run.stdout + run.stderr
words = [int(v) for v in re.findall(r"label: (-?\d+)", log)]
rows = [words[i:i+5] for i in range(0, len(words), 5)]
passed = (len(rows) == 9 and all(len(r) == 5 and r[0] == i and
          r[1] == r[2] and r[3] == r[4] for i, r in enumerate(rows)) and
          "csky_exit_write: exit(0)" in log)
receipt = {
    "result": "PASS" if passed else "FAIL", "rows": rows,
    "cases": len(rows), "elf_sha256": hashlib.sha256(ELF.read_bytes()).hexdigest(),
    "source_sha256": hashlib.sha256((ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_audio_out_db_curve.c").read_bytes()).hexdigest(),
    "scope": "stock/source 0x1000602c return and state +0x12 for nine signed dB values",
    "mmio_reads_rejected": log.count("Invalid read at addr 0xA0B00014"),
    "mmio_writes_rejected": log.count("Invalid write at addr 0xA0B00014"),
    "limits": ["QEMU did not map DAC MMIO; register values/effects are unqualified"],
}
path = HERE / "audio-db-oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(path)
print(receipt["result"], len(rows))
if not passed:
    raise SystemExit(1)

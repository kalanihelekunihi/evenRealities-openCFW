#!/usr/bin/env python3
"""Run the rebuilt same-entry codec-control alias through real publisher peers."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRIOR = ROOT / "g2/analysis/audio-watchdog-callback-closure-2026-10-09"
ELF = Path("/tmp/g2-audio-codec-control-alias-m4.elf")
source = (PRIOR / "verify.py").read_text().split("cases=[]")[0]
old = "receipt=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(receipt['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']"
new = ("receipt={'elf_sha256': '" + hashlib.sha256(ELF.read_bytes()).hexdigest() +
       "'};elf=Path('/tmp/g2-audio-codec-control-alias-m4.elf')")
assert old in source
source = source.replace(old, new)
namespace = {"__file__": str(PRIOR / "verify.py")}
exec(source, namespace)
assert namespace["sym"]["audio_codec_control"] == namespace["sym"]["audio_watchdog_emit_type0"]

cases = []
for argument in (0, 2, 255, 256, 0xffffffff):
    for queue in ("null", "empty", "full"):
        original = namespace["run"](False, "emit_type0", argument, queue)
        alias = namespace["run"](True, "emit_type0", argument, queue)
        assert original == alias, (argument, queue, original, alias)
        cases.append({"argument": argument, "queue": queue, "observed": original})

report = {"matched": len(cases), "total": len(cases), "cases": cases,
          "alias_elf_sha256": hashlib.sha256(ELF.read_bytes()).hexdigest(),
          "prior_fixture_sha256": hashlib.sha256((PRIOR / "verify.py").read_bytes()).hexdigest(),
          "scope": "Complete original emitter and GCC Cortex-M4 same-source alias execute through real original publisher/CMSIS queue. Empty queue stops before thread-flags set; no audio task dispatch or hardware timing."}
Path(__file__).with_name("codec-control-alias-execution.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} codec-control alias comparisons pass")

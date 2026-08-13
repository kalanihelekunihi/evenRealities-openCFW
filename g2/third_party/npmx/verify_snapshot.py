#!/usr/bin/env python3
"""Fail closed on the compact Nordic nPMX source snapshot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST_SHA256 = "a192788fc60c2568154053e1f4144d72e9d4781449d05cea29ab8512c6beba83"
COMMIT = "e1aaec53f456887a7d7b80d82f684d1ac3cb08c8"
TREE = "87fb8b8e3e1068736cd2c02526442e03e67c381c"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict[str, object]:
    manifest = ROOT / "SNAPSHOT.sha256"
    if sha(manifest) != MANIFEST_SHA256:
        raise RuntimeError("nPMX hash manifest changed")
    expected: dict[str, str] = {}
    for line in manifest.read_text().splitlines():
        digest, rel = line.split("  ", 1)
        if rel in expected or len(digest) != 64:
            raise RuntimeError("invalid nPMX hash manifest")
        expected[rel] = digest
    for rel, digest in expected.items():
        path = ROOT / rel
        if not path.is_file() or sha(path) != digest:
            raise RuntimeError(f"nPMX snapshot changed: {rel}")
    provenance = json.loads((ROOT / "PROVENANCE.json").read_text())
    if provenance["upstream"]["selected_commit"] != COMMIT:
        raise RuntimeError("nPMX selected commit changed")
    if provenance["upstream"]["selected_tree"] != TREE:
        raise RuntimeError("nPMX selected tree changed")
    adc = (ROOT / "drivers/src/npmx_adc.c").read_text()
    common = (ROOT / "drivers/src/npmx_common.c").read_text()
    if "static uint16_t msb_register_offset_get" not in adc:
        raise RuntimeError("post-e1aaec ADC discriminator missing")
    if "uint8_t lsb_reg_address = lsb_register_address_get(meas);" not in adc:
        raise RuntimeError("post-e1aaec ADC read split missing")
    if "double a = 1.0, e = a;" not in common:
        raise RuntimeError("pre-53de7af double-promotion discriminator missing")
    if "return -1.49278 + ((2.11263 + (-0.729104 + 0.10969 * variable)" not in common:
        raise RuntimeError("pre-53de7af logarithm discriminator missing")
    if "-1.49278f" in common or "0.6931471806f" in common:
        raise RuntimeError("post-53de7af float constants unexpectedly present")
    return {
        "schema_version": 1,
        "selected_commit": COMMIT,
        "selected_tree": TREE,
        "files": len(expected),
        "byte_identical": True,
        "adc_lower_discriminator": True,
        "common_upper_discriminator": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))

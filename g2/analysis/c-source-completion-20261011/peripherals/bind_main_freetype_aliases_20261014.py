#!/usr/bin/env python3
"""Bind established FreeType and libc symbol names to selected C providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
PRIOR = OUT / "freetype-base-current-receipt.json"
BASE = OUT / "apollo-main-freetype-base-bound.o"
MANIFEST = G2 / "firmware_c/experimental-link-aliases.json"
BOUND = OUT / "apollo-main-freetype-aliases-bound.o"
RECEIPT = OUT / "freetype-aliases-current-receipt.json"
ALIASES = {
    "FT_Stream_Open": "audio_uart_ft_stream_open_path_5675e8",
    "__aeabi_memcpy4": "__aeabi_memcpy",
    "qsort": "audio_uart_ft_qsort_567c4c",
    "strcat": "g2_strcat",
    "strlen": "g2_log_module_length",
    "strncmp": "audio_l2c_strncmp",
    "strncpy": "audio_settings_copy_text",
    "strrchr": "g2_strrchr",
    "g2_norflash_diagnostic_4733ee": "g2_log_transport_queue_failure",
    "g2_norflash_scheduler_state_44906c": "audio_uart_ring_kernel_state",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, *flags):
    output = subprocess.check_output(["arm-none-eabi-nm", *flags, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_FREETYPE_BASE_C_LINK"
    assert sha(BASE) == prior["output_sha256"]
    assert all(json.loads(MANIFEST.read_text())["apollo_main"][name] == target
               for name, target in ALIASES.items())
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "-g", "--defined-only")
    assert len(before) == 569 and set(ALIASES) <= before
    assert set(ALIASES.values()) <= defined and not set(ALIASES) & defined
    args = ["arm-none-eabi-ld", "-r"]
    args += [f"--defsym={name}={target}" for name, target in ALIASES.items()]
    args += [str(BASE), "-o", str(BOUND)]
    subprocess.run(args, cwd=ROOT, check=True, capture_output=True)
    after = symbols(BOUND, "-u")
    assert after == before - set(ALIASES) and len(after) == 559
    receipt = {
        "status": "PASS_CURRENT_MAIN_FREETYPE_ALIAS_LINK",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "alias_manifest": str(MANIFEST.relative_to(ROOT)), "alias_manifest_sha256": sha(MANIFEST),
        "aliases": ALIASES,
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Aliases bind names to existing C definitions; they do not establish whole-function equivalence",
                   "Selected string functions have bounded native probes, but all input domains remain unqualified",
                   "Full image and hardware operation remain unverified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()

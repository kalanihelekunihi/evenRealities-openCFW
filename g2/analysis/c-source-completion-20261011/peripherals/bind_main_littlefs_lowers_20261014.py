#!/usr/bin/env python3
"""Compile three bounded LittleFS lower providers into current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
P = G2 / "analysis/c-source-completion-20261011/peripherals"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-hci-vendor-bound.o"
BASE_RECEIPT = OUT / "hci-vendor-current-receipt.json"
BOUND = OUT / "apollo-main-littlefs-lowers.o"
RECEIPT = OUT / "littlefs-lowers-current-receipt.json"
PROVIDERS = {
    "g2_lfs_mlist_isopen": G2 / "components/audio/file_backend_close_candidate/mlist_isopen.c",
    "g2_lfs_mlist_remove": G2 / "components/audio/file_backend_close_candidate/mlist_remove.c",
    "g2_lfs_memcpy": G2 / "components/audio/file_sync_candidate/byte_copy.c",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, flag):
    output = subprocess.check_output(["arm-none-eabi-nm", flag, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(BASE_RECEIPT.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_HCI_VENDOR_PROVIDER"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    assert len(before) == 646 and set(PROVIDERS) <= before
    for name, result_file, expected, cases in [
        ("g2_lfs_mlist_isopen", P / "mlist-isopen-results.json", "PASS_MLIST_ISOPEN_BOUNDED", 10),
        ("g2_lfs_mlist_remove", P / "mlist-remove-results.json", "PASS_MLIST_REMOVE_BOUNDED", 10),
    ]:
        result = json.loads(result_file.read_text())
        assert result["status"] == expected and result["cases"] == cases
        assert result["source_sha256"] == sha(PROVIDERS[name])
    objects = []
    for name, source in PROVIDERS.items():
        obj = OUT / (name + "-current.o")
        subprocess.run([
            "clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
            "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(obj),
        ], cwd=ROOT, check=True)
        assert nm(obj, "--defined-only") == {name}
        assert not nm(obj, "-u")
        objects.append(obj)
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    assert after == before - set(PROVIDERS)
    assert nm(BOUND, "--defined-only") == nm(BASE, "--defined-only") | set(PROVIDERS)
    receipt = {
        "status": "PASS_CURRENT_MAIN_LITTLEFS_LOWERS",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "providers": [{"symbol": name, "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                       "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj)}
                      for (name, source), obj in zip(PROVIDERS.items(), objects, strict=True)],
        "bounded_oracles": [
            {"path": str((P / "mlist-isopen-results.json").relative_to(ROOT)), "sha256": sha(P / "mlist-isopen-results.json"), "cases": 10},
            {"path": str((P / "mlist-remove-results.json").relative_to(ROOT)), "sha256": sha(P / "mlist-remove-results.json"), "cases": 10},
            {"command": "verify_audio_uart_byte_copy.py", "observed": "PASS_AUDIO_UART_BYTE_COPY 224", "scope": "destination bytes only"},
        ],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)),
        "output_sha256": sha(BOUND),
        "source_complete": False,
        "full_payload_linked": False,
        "limits": ["Copy helper return register is not qualified; current call sites ignore it", "Open-list oracles cover bounded synthetic nodes only", "Final placement and hardware behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after), "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()

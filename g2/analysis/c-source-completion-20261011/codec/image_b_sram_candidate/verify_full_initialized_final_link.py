#!/usr/bin/env python3
"""Final-link placement probe for source-owned B records, not a boot image."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
SELECTED = HERE / "build-ambient-entry-round/receipt.json"
PARTIAL = HERE / "build-full-initialized-ambient-round/receipt.json"
OUT = HERE / "build-full-initialized-ambient-round"
SCRIPT = HERE / "image_b_full_initialized_layout_probe.ld"
EXCLUDE = {"backup_clock_tables.c", "backup_clock_module_select.c",
           "backup_clock_frequency.c", "backup_platform_gate.c",
           "backup_initialized_runtime_data.c", "backup_fft_profile_data.c"}
STEMS = ["clock_single_owner", "initialized_runtime_sections", "fft_profile_sections",
         "sample_app_record", "sample_app_init", "sample_app_begin", "sample_app_leaves",
         "sample_app_event", "sample_app_command", "sample_app_audio_callback", "retained_slots"]
RECORDS = [
    (".gsensor_state", 0x20016f60, 0x10016f60, 4),
    (".audio_runtime_state", 0x20016f64, 0x10016f64, 16),
    (".sample_app_pointer", 0x20016f74, 0x10016f74, 4),
    (".sample_app_record", 0x20016f78, 0x10016f78, 32),
    (".audio_uart_tx", 0x20016f98, 0x10016f98, 32),
    (".imcra_profile", 0x20016fb8, 0x10016fb8, 84),
    (".rifft_profile", 0x2001700c, 0x1001700c, 20),
    (".rfft_profile", 0x20017020, 0x10017020, 20),
    (".kernel_coefficients", 0x20017034, 0x10017034, 88),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target(tool, *args):
    cmd = ["docker", "run", "--rm", "--network=none", "--read-only",
           "--platform", "linux/amd64",
           "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
           "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
           "--mount", f"type=bind,src={OUT},dst=/out", "--tmpfs", "/tmp:rw",
           "opencfw/iar-base:10.10.2-local", f"/tool/bin/csky-abiv2-elf-{tool}", *args]
    return subprocess.run(cmd, text=True, capture_output=True, check=True)


def main():
    selected = json.loads(SELECTED.read_text())
    partial = json.loads(PARTIAL.read_text())
    assert len(selected["units"]) == 233
    assert partial["selected_receipt_sha256"] == sha(SELECTED)
    assert partial["undefined_symbols"] == []
    objects = []
    for unit in selected["units"]:
        if Path(unit["source"]).name in EXCLUDE:
            continue
        source, obj = ROOT / unit["source"], Path(unit["object"])
        assert sha(source) == unit["source_sha256"]
        assert sha(obj) == unit["object_sha256"]
        objects.append(obj)
    assert len(objects) == 227
    for stem, unit in zip(STEMS, partial["experimental_units"], strict=True):
        obj = OUT / f"{stem}.o"
        assert sha(ROOT / unit["source"]) == unit["source_sha256"]
        assert sha(obj) == unit["object_sha256"]
        objects.append(obj)
    elf = OUT / "image_b_full_initialized_layout_probe.elf"
    args = ["-T", f"/repo/{SCRIPT.relative_to(ROOT)}", "-o", f"/out/{elf.name}"]
    args.extend(f"/repo/{obj.relative_to(ROOT)}" for obj in objects)
    link = target("ld", *args)
    sections = target("objdump", "-h", f"/out/{elf.name}").stdout
    found = {}
    for line in sections.splitlines():
        cols = line.split()
        if len(cols) >= 7 and cols[0].isdigit():
            found[cols[1]] = tuple(int(cols[i], 16) for i in (2, 3, 4))
    for name, vma, lma, size in RECORDS:
        assert found[name] == (size, vma, lma), (name, found.get(name))
    assert sum(x[3] for x in RECORDS) == 300
    assert found[".text"][1] == 0x10003100
    assert found[".text"][0] + 0x10003100 <= found[".rodata"][1]
    assert found[".bss"][0] == 0x1670c
    report = {
        "selected_receipt_sha256": sha(SELECTED),
        "partial_receipt_sha256": sha(PARTIAL),
        "object_count": len(objects),
        "elf": str(elf.relative_to(ROOT)),
        "elf_sha256": sha(elf),
        "source_owned_normal_data_bytes_at_distinct_lma_vma": 300,
        "source_text_bytes": found[".text"][0],
        "source_rodata_bytes": found[".rodata"][0],
        "source_bss_bytes": found[".bss"][0],
        "stock_bss_clear_bytes": 0x2002d79c - 0x20017090,
        "linker_warnings": link.stderr.strip().splitlines(),
        "status": "PASS_LAYOUT_ONLY",
        "source_complete": False,
        "bootable": False,
        "limits": ["The linker reserves the authenticated 91916-byte BSS clear interval, but only 8 bytes are currently represented by typed C declarations; field ownership remains incomplete.",
                   "Vector/reset packaging and stock-loader alias execution are unqualified.",
                   "Experimental app callbacks lack whole-body original/source effect equivalence."],
    }
    (HERE / "full-initialized-final-link-receipt.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"300-byte final LMA/VMA placement PASS, ELF {report['elf_sha256']}")


if __name__ == "__main__":
    main()

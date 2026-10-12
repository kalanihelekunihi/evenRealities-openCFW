"""Finite original/source CK804EF process comparison in pinned QEMU.

The stock .incbin appears only in the oracle ELF. The source ELF links the
experimental C candidate; its FP-environment witnesses fail if reached.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
QEMU = ROOT / "g2/build/offline-xuantie-csky-dsp-20261009T201800Z/qemu-system-cskyv2"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
BUILD = HERE / "build-native-oracle-correction-round/receipt.json"
OUT = HERE / "native-oracle-run"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: list[str], *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(args, text=True, capture_output=True, timeout=60)
    if p.returncode and not allow_failure:
        raise RuntimeError(f"{args!r}: {p.returncode}\n{p.stderr}\n{p.stdout}")
    return p


def tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return run([
        "docker", "run", "--rm", "--network=none", "--platform", "linux/amd64",
        "-v", f"{ROOT}:/repo", "-v", f"{TOOL}:/tool:ro",
        "-w", "/repo/" + str(HERE.relative_to(ROOT)),
        "opencfw/iar-base:10.10.2-local", *args,
    ])


def main() -> None:
    OUT.mkdir(exist_ok=True)
    selected = json.loads(BUILD.read_text())
    assert selected["source_complete"] is False
    assert sha(STOCK) == selected["image_sha256"]
    objects = ["/repo/" + str(Path(u["object"]).relative_to(ROOT))
               for u in selected["units"]]
    tool(["/tool/bin/csky-abiv2-elf-ar", "rcs",
          "/repo/" + str((OUT / "source-corrected.a").relative_to(ROOT)),
          *objects])
    common = ["/tool/bin/csky-abiv2-elf-gcc", "-mcpu=ck804ef",
              "-mhard-float", "-nostdlib", "-nostartfiles"]
    for mode in ("original", "source"):
        script = "process_native_oracle.ld" if mode == "original" else "process_source_oracle.ld"
        cmd = common + ["-Wl,-T," + script,
                        "-o", "/repo/" + str((OUT / f"{mode}.elf").relative_to(ROOT)),
                        "process_native_oracle_start.S", "process_native_oracle_main.c"]
        if mode == "original":
            cmd += ["process_native_oracle_stock.S"]
        else:
            cmd[1:1] = ["-DSOURCE_MODE"]
            cmd += ["process_oracle_unexpected_fp.S",
                    "/repo/" + str((OUT / "source-corrected.a").relative_to(ROOT))]
        tool(cmd)
    observations = {}
    for mode in ("original", "source"):
        elf = OUT / f"{mode}.elf"
        p = run([
            "docker", "run", "--rm", "--network=none",
            "-v", f"{ROOT}:/repo", "-w", "/repo",
            "opencfw/qemu-csky-builddeps:20261009t201800",
            "sh", "-lc",
            "timeout 12s /repo/" + str(QEMU.relative_to(ROOT)) +
            " -M virt -m 1G -cpu ck804ef -nographic -monitor none -kernel /repo/" +
            str(elf.relative_to(ROOT)) +
            " -d guest_errors -D /tmp/process.log; result=$?; cat /tmp/process.log; exit $result",
        ])
        lines = [line.strip() for line in p.stdout.splitlines() if line.strip()]
        assert lines == ["label: 3", "label: 1", "label: 1000",
                         "label: 2000", "label: 90", "label: 0",
                         "csky_exit_write: exit(0)"], lines
        observations[mode] = {"elf_sha256": sha(elf), "trace": lines}
    result = {
        "stock_sha256": sha(STOCK),
        "source_receipt_sha256": sha(BUILD),
        "qemu_sha256": sha(QEMU),
        "cases": ["zero stage/frame and zero output", "zero stage/frame with tail copy"],
        "observations": observations,
        "result": "PASS",
        "limit": "Two finite QEMU paths; no active stage/frame/channel, DSP numerical, FP exception, original four-register RAM-binding, hardware, or whole-image equivalence proof.",
    }
    (OUT / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

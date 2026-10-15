#!/usr/bin/env python3
"""Compile upstream FreeType base and bitmap against recovered G2 configuration."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
PRIOR = OUT / "freetype-modules-current-receipt.json"
BASE = OUT / "apollo-main-freetype-modules-bound.o"
SOURCES = (ROOT / "third-party/upstream/freetype/src/base/ftbase.c",
           ROOT / "third-party/upstream/freetype/src/base/ftbitmap.c")
OBJECTS = OUT / "freetype-base-current"
BOUND = OUT / "apollo-main-freetype-base-bound.o"
RECEIPT = OUT / "freetype-base-current-receipt.json"
PINNED = G2 / "build/c-firmware/20261013/peripherals-root-freetype-upstream-modules-round411/receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    output = subprocess.check_output(["arm-none-eabi-nm", *flags, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_FREETYPE_MODULE_C_LINK"
    assert sha(BASE) == prior["output_sha256"]
    assert subprocess.check_output(
        ["git", "-C", str(ROOT / "third-party/upstream/freetype"), "rev-parse", "HEAD"],
        text=True).strip() == prior["freetype_submodule_commit"]
    before = names(BASE, "-u")
    assert len(before) == 645
    pinned = json.loads(PINNED.read_text())
    template = list(pinned["images"]["apollo_main"]["experimental_compile"][0]["argv"])
    assert template[0] == "clang" and "-DFT2_BUILD_LIBRARY" in template
    OBJECTS.mkdir(parents=True, exist_ok=True)
    objects = []
    rows = []
    for index, source in enumerate(SOURCES):
        obj = OBJECTS / f"base-{index:02d}.o"
        dep = OBJECTS / f"base-{index:02d}.d"
        source_sha = sha(source)
        argv = list(template)
        argv[argv.index("-c") + 1] = str(source)
        argv[argv.index("-MF") + 1] = str(dep)
        argv[argv.index("-o") + 1] = str(obj)
        subprocess.run(argv, cwd=ROOT, check=True, capture_output=True)
        assert sha(source) == source_sha
        objects.append(obj)
        rows.append({"source": str(source.relative_to(ROOT)), "source_sha256": source_sha,
                     "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj)})
    current_exports = names(BASE, "-g", "--defined-only")
    added_exports = set()
    for obj in objects:
        exports = names(obj, "-g", "--defined-only")
        assert not (exports & current_exports) and not (exports & added_exports)
        added_exports |= exports
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(BOUND)], cwd=ROOT, check=True, capture_output=True)
    after = names(BOUND, "-u")
    resolved, added = before - after, after - before
    assert len(after) == 569 and len(resolved) == 80
    assert added == {"FT_Stream_Open", "strcat", "strncpy", "strrchr"}
    receipt = {
        "status": "PASS_CURRENT_MAIN_FREETYPE_BASE_C_LINK",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "freetype_submodule_commit": prior["freetype_submodule_commit"],
        "source_units": rows,
        "imports_resolved": sorted(resolved), "imports_added": sorted(added),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Upstream source and recovered configuration compiled; base callback behavior is not native-qualified",
                   "FT_Stream_Open and three libc helpers remain explicit imports",
                   "Full payload layout and hardware behavior remain unverified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()

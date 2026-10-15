#!/usr/bin/env python3
"""Build FreeType bundled gzip as a freestanding Main dependency."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
PRIOR = OUT / "freetype-aliases-current-receipt.json"
BASE = OUT / "apollo-main-freetype-aliases-bound.o"
SOURCE = ROOT / "third-party/upstream/freetype/src/gzip/ftgzip.c"
PINNED = G2 / "build/c-firmware/20261013/peripherals-root-freetype-upstream-modules-round411/receipt.json"
OBJECT = OUT / "freetype-gzip-current.o"
BOUND = OUT / "apollo-main-freetype-gzip-bound.o"
RECEIPT = OUT / "freetype-gzip-current-receipt.json"
PROVIDER = "FT_Gzip_Uncompress"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    output = subprocess.check_output(["arm-none-eabi-nm", *flags, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_FREETYPE_ALIAS_LINK"
    assert sha(BASE) == prior["output_sha256"]
    assert subprocess.check_output(
        ["git", "-C", str(ROOT / "third-party/upstream/freetype"), "rev-parse", "HEAD"],
        text=True).strip() == "86bc8a95056c97a810986434a3f268cbe67f2902"
    before = names(BASE, "-u")
    assert len(before) == 559 and PROVIDER in before
    source_sha = sha(SOURCE)
    pinned = json.loads(PINNED.read_text())
    template = list(pinned["images"]["apollo_main"]["experimental_compile"][0]["argv"])
    argv = template[:template.index("-MD")]
    assert argv[0] == "clang" and "-DFT2_BUILD_LIBRARY" in argv
    argv += ["-DNO_ERRNO_H", "-c", str(SOURCE), "-o", str(OBJECT)]
    subprocess.run(argv, cwd=ROOT, check=True, capture_output=True)
    assert sha(SOURCE) == source_sha
    assert PROVIDER in names(OBJECT, "-g", "--defined-only")
    assert not names(OBJECT, "-g", "--defined-only") & names(BASE, "-g", "--defined-only")
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(OBJECT), "-o", str(BOUND)],
                   cwd=ROOT, check=True, capture_output=True)
    after = names(BOUND, "-u")
    assert after == before - {PROVIDER} and len(after) == 558
    receipt = {
        "status": "PASS_CURRENT_MAIN_FREETYPE_GZIP_C_LINK",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": source_sha,
        "object": str(OBJECT.relative_to(ROOT)), "object_sha256": sha(OBJECT),
        "compile_flag": "-DNO_ERRNO_H",
        "freetype_submodule_commit": "86bc8a95056c97a810986434a3f268cbe67f2902",
        "imports_resolved": [PROVIDER], "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Bundled upstream gzip compiles and links; native decompression equivalence remains unverified",
                   "Full image and hardware operation remain unverified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()

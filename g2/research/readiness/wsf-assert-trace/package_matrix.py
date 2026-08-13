#!/usr/bin/env python3
import csv
import hashlib
import pathlib
import shutil
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
out = root / "out"
artifact = root / "artifact"
if artifact.exists():
    shutil.rmtree(artifact)
artifact.mkdir()

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def blob(path):
    data = pathlib.Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

wsf = root / "AmbiqSuite-R2.5.1/third_party/cordio/wsf"
src = wsf / "sources/port/freertos"
with open(artifact/"source-identities.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("identity", "path_or_release", "bytes", "sha256", "git_blob_sha1", "qualification"))
    for name in ("wsf_assert.c", "wsf_trace.c"):
        path = src/name
        writer.writerow(("selected_implementation", f"AmbiqSuite-R2.5.1/third_party/cordio/wsf/sources/port/freertos/{name}", path.stat().st_size, sha(path), blob(path), "authenticated official archive source; proprietary; excluded from artifact"))
    writer.writerow(("archive", "AmbiqSuite-R2.5.1-s3.zip", 200161418, "87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133", "", "authenticated official archive; not redistributed"))
    writer.writerow(("stock_firmware", "g2-2.2.6.10 ota_s200_firmware_ota.bin", 3523396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863", "", "authenticated stock image; excluded from artifact"))

def dependencies(name):
    text = (out/f"deps/{name}.d").read_text().replace("\\\n", " ")
    return list(dict.fromkeys(text.split(":", 1)[1].split()))

with open(artifact/"include-closure.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("translation_unit", "class", "path", "bytes", "sha256"))
    for unit in ("wsf_assert", "wsf_trace"):
        for name in dependencies(unit):
            if name.startswith("/usr/lib/gcc/"):
                writer.writerow((unit, "compiler_builtin", name, "", "recorded by pinned container identity"))
                continue
            path = root/name
            kind = "stock_abi_cleanroom_shim" if name.startswith("shim/") else "ambiqsuite_2.5.1_archive"
            writer.writerow((unit, kind, name, path.stat().st_size, sha(path)))

with open(artifact/"source-config-variants.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("variant", "compile_macros", "status", "evidence"))
    writer.writerow(("stockabi_1024", "AM_DEBUG_PRINTF=1;WSF_TRACE_ENABLED=1;WSF_TOKEN_ENABLED=0;WSF_ASSERT_ENABLED=1;AM_PRINTF_BUFSIZE=1024", "matrix-selected", "stock WsfTrace reserves 0x400 bytes and calls vsprintf, printf, WsfAssert, printf in official source order"))
    writer.writerow(("archive_default_256", "AM_PRINTF_BUFSIZE=256", "eliminated without matrix expansion", "contradicted by stock 0x400-byte local buffer"))
    writer.writerow(("tokenized_trace", "WSF_TRACE_ENABLED=0;WSF_TOKEN_ENABLED=1", "eliminated", "stock has printf call graph and 126 WsfTrace callers; no token-ring body at bounded entry"))
    writer.writerow(("upstream_spin_assert", "official wsf_assert.c body", "compiled but downstream-drifted", "stock body adds EasyLogger diagnostics, hook handling, and fail-stop seam absent from official source"))

common = "-std=c11 -mcpu=cortex-m55 -mthumb -mno-unaligned-access -ffreestanding -fno-lto -fno-builtin -ffunction-sections -fdata-sections -fomit-frame-pointer -fno-unwind-tables -fno-asynchronous-unwind-tables -DAM_DEBUG_PRINTF=1 -DWSF_TRACE_ENABLED=1 -DWSF_TOKEN_ENABLED=0 -DWSF_ASSERT_ENABLED=1 -DAM_PRINTF_BUFSIZE=1024 -Wall -Wextra -Werror -Wno-unused-parameter"
configs = {
    "O0": "-O0", "O1": "-O1", "Og": "-Og", "Og_nosibling": "-Og -fno-optimize-sibling-calls",
    "O2": "-O2", "O2_noinline": "-O2 -fno-inline -fno-inline-functions -fno-inline-small-functions",
    "O3": "-O3", "O3_noinline": "-O3 -fno-inline -fno-inline-functions -fno-inline-small-functions",
    "Os": "-Os", "Os_noinline": "-Os -fno-inline -fno-inline-functions -fno-inline-small-functions",
    "Os_nosibling": "-Os -fno-optimize-sibling-calls", "Oz": "-Oz", "Oz_nosibling": "-Oz -fno-optimize-sibling-calls",
}
with open(artifact/"compiler-configs.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("config", "common_flags", "profile_flags"))
    for name, flags in configs.items():
        writer.writerow((name, common, flags))

for name in ("comparison-ledger.tsv", "config-summary.tsv", "best-size-per-function.tsv", "build-results.tsv", "matrix-timing.txt", "dependency-timing.txt", "toolchain.txt", "source-api-build-sizes.tsv"):
    shutil.copy2(out/name, artifact/name)
for name in ("functions.tsv", "closure_stubs.c", "normalize_disassembly.py", "run_matrix.py", "package_matrix.py"):
    shutil.copy2(root/"input"/name, artifact/name)
for name in ("am_util_debug.h", "am_util_stdio.h", "string.h", "stdio.h", "stdbool.h"):
    shutil.copy2(root/"shim"/name, artifact/name)

rows = list(csv.DictReader(open(out/"comparison-ledger.tsv"), delimiter="\t"))
with open(artifact/"stock-functions.tsv", "w", newline="") as f:
    fields = ("function", "start", "end", "stock_size", "stock_sha256", "stock_normalized_sha256", "evidence")
    writer = csv.DictWriter(f, fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    seen = set()
    for row in rows:
        if row["function"] not in seen:
            seen.add(row["function"])
            writer.writerow({key: row[key] for key in fields})

with open(artifact/"provider-closure.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("translation_unit", "symbol", "resolution"))
    for symbol in (out/"stockabi_1024__Os_nosibling/assert.undefined").read_text().splitlines():
        writer.writerow(("wsf_assert.c", symbol, "resolved by companion/source or closure"))
    for symbol in (out/"stockabi_1024__Os_nosibling/trace.undefined").read_text().splitlines():
        writer.writerow(("wsf_trace.c", symbol, "resolved by companion/source or clean-room logger stub"))
    writer.writerow(("linked_closure", "(none)", "zero undefined symbols in all 13 profiles"))

build = list(csv.DictReader(open(out/"build-results.tsv"), delimiter="\t"))
summary = list(csv.DictReader(open(out/"config-summary.tsv"), delimiter="\t"))
best = min(summary, key=lambda row: (int(row["aggregate_abs_size_delta"]), -int(row["exact_size"])))
elapsed = int((out/"matrix-timing.txt").read_text().split("=", 1)[1])
compile_total = sum(int(row["compile_ns"]) for row in build)
link_total = sum(int(row["link_ns"]) for row in build)
raw = sum(row["raw_match"] == "yes" for row in rows)
normalized = sum(row["strict_normalized_match"] == "yes" for row in rows)
(artifact/"README.txt").write_text(f'''OpenCFW Lorelei Cordio wsf_assert.c/wsf_trace.c readiness and structural matrix

Scope
-----
Scratch-only comparison against authenticated G2 stock firmware. Proprietary AmbiqSuite source, stock firmware, generated objects, raw function bytes, and disassembly are excluded. This artifact contains identities, exact flags, clean-room ABI headers/stubs, closure and comparison ledgers, timings, and checksums.

Bounded stock bodies
--------------------
WsfTrace [0x0052A63C,0x0052A672) is 54 bytes. It has 126 direct BL callers, the retained wsf_trace.c path and line-137 literal, an exact 1024-byte local buffer, and the official source provider order: am_util_stdio_vsprintf, am_util_stdio_printf, conditional WsfAssert, final printf. WsfPacketTrace is compiled by the source but dead-stripped/unbounded in stock.

WsfAssert [0x00569A44,0x00569ADE) is 154 bytes with a sole direct BL from WsfTrace, a clean next-function boundary, retained wsf_assert.c path, and EasyLogger assertion literals/providers. This is a downstream-expanded implementation: the official 2.5.1 source is only a debugger-escape spin loop. Its structural comparison is an implementation-drift baseline, not a plausible compiler identity match.

Configuration and closure
-------------------------
The selected trace configuration pins AM_DEBUG_PRINTF=1, WSF_TRACE_ENABLED=1, WSF_TOKEN_ENABLED=0, WSF_ASSERT_ENABLED=1, and AM_PRINTF_BUFSIZE=1024. Archive-default 256 bytes and tokenized tracing are ruled out by stock. Clean-room Ambiq logger headers preserve the official function ABI without importing SDK utility implementation. Every one of 13 profiles links to zero undefined symbols.

Results
-------
Thirteen compiler profiles x two bounded functions produced {len(rows)} comparison rows in {elapsed} ns wall-clock; summed compile {compile_total} ns and link {link_total} ns. Raw matches: {raw}; strict normalized matches: {normalized}. Best aggregate lane is {best['lane']} with {best['aggregate_abs_size_delta']} bytes total absolute size delta and {best['exact_size']}/2 exact sizes. See best-size-per-function.tsv for the per-function result.

Interpretation
--------------
WsfTrace is a strong exact-source/config mapping even if GCC does not reproduce IAR bytes. WsfAssert proves the same retained translation-unit identity but also a material downstream EasyLogger augmentation. The next productive step is to recover that small downstream WsfAssert source overlay from the already bounded EasyLogger ABI, then run the licensed IAR profile. Do not assign a stock address to WsfPacketTrace without independent caller or stored-pointer evidence.
''')

sumfile = artifact/"SHA256SUMS"
lines = []
for path in sorted(p for p in artifact.iterdir() if p.is_file() and p != sumfile):
    lines.append(f"{sha(path)}  {path.name}")
sumfile.write_text("\n".join(lines) + "\n")
tar = root/"wsf-assert-trace-readiness-matrix-artifact.tar.gz"
subprocess.run(["tar", "--sort=name", "--mtime=@0", "--owner=0", "--group=0", "--numeric-owner", "-czf", str(tar), "-C", str(root), "artifact"], check=True)
(root/"wsf-assert-trace-readiness-matrix-artifact.tar.gz.sha256").write_text(f"{sha(tar)}  {tar.name}\n")
print("tar_sha256", sha(tar), "tar_bytes", tar.stat().st_size, "elapsed", elapsed, "compile_total", compile_total, "link_total", link_total, "best", best["lane"], best["aggregate_abs_size_delta"])
for name in ("comparison-ledger.tsv", "config-summary.tsv", "best-size-per-function.tsv", "include-closure.tsv", "source-config-variants.tsv", "source-api-build-sizes.tsv", "provider-closure.tsv", "source-identities.tsv"):
    print(name, sha(artifact/name))

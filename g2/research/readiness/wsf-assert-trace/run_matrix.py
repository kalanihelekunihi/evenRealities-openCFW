#!/usr/bin/env python3
import csv
import hashlib
import os
import pathlib
import re
import subprocess
import sys
import time

root = pathlib.Path(sys.argv[1]).resolve()
wsf = root / "AmbiqSuite-R2.5.1/third_party/cordio/wsf"
src = wsf / "sources/port/freertos"

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

assert sha(src / "wsf_assert.c") == "f51b7b1441cef0aaed55fdaf84680684813d1fe6182245660e8b21313ce54b1f"
assert sha(src / "wsf_trace.c") == "677ad691762aebf972304cf3720a1d7d7ca3eb77077231f52d68e5658cd7d918"

functions = list(csv.DictReader(open(root / "input/functions.tsv"), delimiter="\t"))
configs = {
    "O0": "-O0",
    "O1": "-O1",
    "Og": "-Og",
    "Og_nosibling": "-Og -fno-optimize-sibling-calls",
    "O2": "-O2",
    "O2_noinline": "-O2 -fno-inline -fno-inline-functions -fno-inline-small-functions",
    "O3": "-O3",
    "O3_noinline": "-O3 -fno-inline -fno-inline-functions -fno-inline-small-functions",
    "Os": "-Os",
    "Os_noinline": "-Os -fno-inline -fno-inline-functions -fno-inline-small-functions",
    "Os_nosibling": "-Os -fno-optimize-sibling-calls",
    "Oz": "-Oz",
    "Oz_nosibling": "-Oz -fno-optimize-sibling-calls",
}

firmware = (root / "stock-firmware.bin").read_bytes()
base = 0x437FE0
for fn in functions:
    start, end = int(fn["start"], 0), int(fn["end"], 0)
    (root / f"stock/{fn['stock_name']}.bin").write_bytes(firmware[start-base:end-base])

common = " ".join([
    "-std=c11", "-mcpu=cortex-m55", "-mthumb", "-mno-unaligned-access",
    "-ffreestanding", "-fno-lto", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fomit-frame-pointer", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-DAM_DEBUG_PRINTF=1",
    "-DWSF_TRACE_ENABLED=1", "-DWSF_TOKEN_ENABLED=0", "-DWSF_ASSERT_ENABLED=1",
    "-DAM_PRINTF_BUFSIZE=1024", "-Wall", "-Wextra", "-Werror",
    "-Wno-unused-parameter",
])

script = f'''set -eu
wsf=AmbiqSuite-R2.5.1/third_party/cordio/wsf
src="$wsf/sources/port/freertos"
inc="-Ishim -I$src -I$wsf/include"
common="{common}"
mkdir -p out/deps
: > out/dependency-timing.txt
printf 'lane\tconfig\tcompile_ns\tlink_ns\tassert_object_sha256\ttrace_object_sha256\tstubs_sha256\tlinked_sha256\tassert_module_undefined\ttrace_module_undefined\tlinked_undefined\n' > out/build-results.tsv
t0=$(date +%s%N)
arm-none-eabi-gcc $common $inc -M "$src/wsf_assert.c" > out/deps/wsf_assert.d
arm-none-eabi-gcc $common $inc -M "$src/wsf_trace.c" > out/deps/wsf_trace.d
t1=$(date +%s%N)
printf 'dependency_ns=%s\n' "$((t1-t0))" >> out/dependency-timing.txt
'''

for config, flags in configs.items():
    lane = f"stockabi_1024__{config}"
    script += f'''od=out/{lane}; mkdir -p "$od"
t0=$(date +%s%N)
arm-none-eabi-gcc $common {flags} $inc -c "$src/wsf_assert.c" -o "$od/wsf_assert.o" 2>"$od/wsf_assert.stderr"
arm-none-eabi-gcc $common {flags} $inc -c "$src/wsf_trace.c" -o "$od/wsf_trace.o" 2>"$od/wsf_trace.stderr"
arm-none-eabi-gcc $common {flags} $inc -c input/closure_stubs.c -o "$od/closure_stubs.o" 2>"$od/closure_stubs.stderr"
t1=$(date +%s%N)
arm-none-eabi-nm -u "$od/wsf_assert.o" | awk '{{print $NF}}' | sort -u > "$od/assert.undefined"
arm-none-eabi-nm -u "$od/wsf_trace.o" | awk '{{print $NF}}' | sort -u > "$od/trace.undefined"
arm-none-eabi-gcc -mcpu=cortex-m55 -mthumb -nostdlib -Wl,--gc-sections -Wl,-e,open_cfw_wsf_assert_trace_closure_root "$od/wsf_assert.o" "$od/wsf_trace.o" "$od/closure_stubs.o" -lgcc -o "$od/closure.elf"
t2=$(date +%s%N)
arm-none-eabi-nm -u "$od/closure.elf" | awk '{{print $NF}}' | sort -u > "$od/linked.undefined"
arm-none-eabi-nm -S --size-sort "$od/wsf_assert.o" > "$od/wsf_assert.nm"
arm-none-eabi-nm -S --size-sort "$od/wsf_trace.o" > "$od/wsf_trace.nm"
arm-none-eabi-objcopy --dump-section .text.WsfAssert="$od/WsfAssert.bin" "$od/wsf_assert.o"
arm-none-eabi-objcopy --dump-section .text.WsfTrace="$od/WsfTrace.bin" "$od/wsf_trace.o"
arm-none-eabi-objcopy --dump-section .text.WsfPacketTrace="$od/WsfPacketTrace.bin" "$od/wsf_trace.o"
arm-none-eabi-objdump -dr -j .text.WsfAssert "$od/wsf_assert.o" > "$od/WsfAssert.disasm"
arm-none-eabi-objdump -dr -j .text.WsfTrace "$od/wsf_trace.o" > "$od/WsfTrace.disasm"
asha=$(sha256sum "$od/wsf_assert.o" | awk '{{print $1}}'); tsha=$(sha256sum "$od/wsf_trace.o" | awk '{{print $1}}'); ssha=$(sha256sum "$od/closure_stubs.o" | awk '{{print $1}}'); esha=$(sha256sum "$od/closure.elf" | awk '{{print $1}}'); au=$(wc -l < "$od/assert.undefined" | tr -d ' '); tu=$(wc -l < "$od/trace.undefined" | tr -d ' '); lu=$(wc -l < "$od/linked.undefined" | tr -d ' ')
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' '{lane}' '{config}' "$((t1-t0))" "$((t2-t1))" "$asha" "$tsha" "$ssha" "$esha" "$au" "$tu" "$lu" >> out/build-results.tsv
'''

docker = [
    "docker", "run", "--rm", "-i", "--network", "none", "--read-only",
    "--security-opt", "label=disable", "--tmpfs", "/tmp:exec",
    "--user", f"{os.getuid()}:{os.getgid()}", "-w", "/work", "-e", "TMPDIR=/tmp",
    "-v", f"{root}:/work", "opencfw-arm-gcc:13.2-rel1", "sh", "-s",
]
t0 = time.time_ns()
subprocess.run(docker, input=script, text=True, check=True)
elapsed = time.time_ns() - t0

compiler = subprocess.check_output(docker[:-2] + ["arm-none-eabi-gcc", "--version"], text=True)
binutils = subprocess.check_output(docker[:-2] + ["arm-none-eabi-objdump", "--version"], text=True)
image_identity = subprocess.check_output(["docker", "image", "inspect", "--format", "{{.Id}}", "opencfw-arm-gcc:13.2-rel1"], text=True).strip()
(root/"out/toolchain.txt").write_text(
    "container_tag=opencfw-arm-gcc:13.2-rel1\n"
    f"container_image_id={image_identity}\n"
    f"compiler={compiler.splitlines()[0]}\n"
    f"binutils={binutils.splitlines()[0]}\n"
)

stock_script = "set -eu\n"
for fn in functions:
    stock_script += f"arm-none-eabi-objdump -D -b binary -marm -Mforce-thumb --adjust-vma={fn['start']} stock/{fn['stock_name']}.bin > stock/{fn['stock_name']}.disasm\n"
subprocess.run(docker, input=stock_script, text=True, check=True)

norm = root / "input/normalize_disassembly.py"
for config in configs:
    lane = f"stockabi_1024__{config}"
    for fn in functions:
        name = fn["stock_name"]
        subprocess.run([sys.executable, str(norm), str(root/f"out/{lane}/{name}.disasm"), str(root/f"out/{lane}/{name}.norm")], check=True)
for fn in functions:
    name = fn["stock_name"]
    subprocess.run([sys.executable, str(norm), str(root/f"stock/{name}.disasm"), str(root/f"stock/{name}.norm")], check=True)

build = {r["lane"]: r for r in csv.DictReader(open(root/"out/build-results.tsv"), delimiter="\t")}
rows = []
for config in configs:
    lane = f"stockabi_1024__{config}"
    record = build[lane]
    for fn in functions:
        name = fn["stock_name"]
        candidate = root/f"out/{lane}/{name}.bin"
        stock = root/f"stock/{name}.bin"
        candidate_norm = root/f"out/{lane}/{name}.norm"
        stock_norm = root/f"stock/{name}.norm"
        cb, sb = candidate.read_bytes(), stock.read_bytes()
        rows.append({
            "lane": lane, "config": config, "function": name,
            "start": fn["start"], "end": fn["end"], "candidate_symbol": fn["candidate_symbol"],
            "evidence": fn["evidence"], "candidate_size": len(cb), "stock_size": len(sb),
            "size_delta": len(cb)-len(sb), "raw_match": "yes" if cb == sb else "no",
            "strict_normalized_match": "yes" if candidate_norm.read_bytes() == stock_norm.read_bytes() else "no",
            "candidate_sha256": sha(candidate), "stock_sha256": sha(stock),
            "candidate_normalized_sha256": sha(candidate_norm), "stock_normalized_sha256": sha(stock_norm),
            "compile_ns": record["compile_ns"], "link_ns": record["link_ns"],
            "assert_object_sha256": record["assert_object_sha256"], "trace_object_sha256": record["trace_object_sha256"],
            "linked_sha256": record["linked_sha256"],
        })

with open(root/"out/comparison-ledger.tsv", "w", newline="") as f:
    writer = csv.DictWriter(f, list(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
with open(root/"out/config-summary.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("lane", "config", "functions", "exact_size", "aggregate_abs_size_delta", "raw_matches", "strict_normalized_matches"))
    for config in configs:
        lane = f"stockabi_1024__{config}"
        selected = [r for r in rows if r["lane"] == lane]
        writer.writerow((lane, config, len(selected), sum(r["size_delta"] == 0 for r in selected), sum(abs(r["size_delta"]) for r in selected), sum(r["raw_match"] == "yes" for r in selected), sum(r["strict_normalized_match"] == "yes" for r in selected)))
with open(root/"out/best-size-per-function.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("function", "stock_size", "best_abs_delta", "best_rows"))
    for fn in functions:
        selected = [r for r in rows if r["function"] == fn["stock_name"]]
        best = min(abs(r["size_delta"]) for r in selected)
        picks = ",".join(f"{r['lane']}:{r['candidate_size']}({r['size_delta']:+d})" for r in selected if abs(r["size_delta"]) == best)
        writer.writerow((fn["stock_name"], selected[0]["stock_size"], best, picks))
with open(root/"out/source-api-build-sizes.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("lane", "config", "translation_unit", "symbol", "size"))
    for config in configs:
        lane = f"stockabi_1024__{config}"
        for unit in ("wsf_assert", "wsf_trace"):
            for line in (root/f"out/{lane}/{unit}.nm").read_text().splitlines():
                match = re.match(r"^[0-9a-f]+\s+([0-9a-f]+)\s+T\s+(Wsf\S+)$", line)
                if match:
                    writer.writerow((lane, config, unit, match.group(2), int(match.group(1), 16)))
(root/"out/matrix-timing.txt").write_text(f"matrix_elapsed_ns={elapsed}\n")
print("root", root, "rows", len(rows), "elapsed_ns", elapsed, "raw", sum(r["raw_match"] == "yes" for r in rows), "normalized", sum(r["strict_normalized_match"] == "yes" for r in rows), "ledger_sha256", sha(root/"out/comparison-ledger.tsv"))

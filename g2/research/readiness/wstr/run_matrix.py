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
wsf = root/"AmbiqSuite-R2.5.1/third_party/cordio/wsf"
source = wsf/"sources/util/wstr.c"

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

assert sha(source) == "7b226d9ebdbab4d305da843c4fd865c64f408f4376551499f94fcd0451dd6452"
functions = list(csv.DictReader(open(root/"input/functions.tsv"), delimiter="\t"))
configs = {
    "O0":"-O0", "O1":"-O1", "Og":"-Og", "Og_nosibling":"-Og -fno-optimize-sibling-calls",
    "O2":"-O2", "O2_noinline":"-O2 -fno-inline -fno-inline-functions -fno-inline-small-functions",
    "O3":"-O3", "O3_noinline":"-O3 -fno-inline -fno-inline-functions -fno-inline-small-functions",
    "Os":"-Os", "Os_noinline":"-Os -fno-inline -fno-inline-functions -fno-inline-small-functions",
    "Os_nosibling":"-Os -fno-optimize-sibling-calls", "Oz":"-Oz", "Oz_nosibling":"-Oz -fno-optimize-sibling-calls",
}
common = "-std=c11 -mcpu=cortex-m55 -mthumb -mno-unaligned-access -ffreestanding -fno-lto -fno-builtin -ffunction-sections -fdata-sections -fomit-frame-pointer -fno-unwind-tables -fno-asynchronous-unwind-tables -Wall -Wextra -Werror"

firmware = (root/"stock-firmware.bin").read_bytes()
base = 0x437FE0
for fn in functions:
    start, end = int(fn["start"],0), int(fn["end"],0)
    (root/f"stock/{fn['stock_name']}.bin").write_bytes(firmware[start-base:end-base])

docker = ["docker","run","--rm","-i","--network","none","--read-only","--security-opt","label=disable","--tmpfs","/tmp:exec","--user",f"{os.getuid()}:{os.getgid()}","-w","/work","-e","TMPDIR=/tmp","-v",f"{root}:/work","opencfw-arm-gcc:13.2-rel1","sh","-s"]
script = f'''set -eu
wsf=AmbiqSuite-R2.5.1/third_party/cordio/wsf
inc="-Ishim -I$wsf/sources/util -I$wsf/sources/port/freertos -I$wsf/include"
common="{common}"
mkdir -p out/deps
t0=$(date +%s%N); arm-none-eabi-gcc $common $inc -M $wsf/sources/util/wstr.c > out/deps/wstr.d; t1=$(date +%s%N); printf 'dependency_ns=%s\n' "$((t1-t0))" > out/dependency-timing.txt
printf 'lane\tconfig\tcompile_ns\tlink_ns\tobject_sha256\troot_sha256\tlinked_sha256\tmodule_undefined\tlinked_undefined\n' > out/build-results.tsv
'''
for config, flags in configs.items():
    lane = f"ambiq_exact__{config}"
    script += f'''od=out/{lane}; mkdir -p "$od"
t0=$(date +%s%N)
arm-none-eabi-gcc $common {flags} $inc -c $wsf/sources/util/wstr.c -o "$od/wstr.o"
arm-none-eabi-gcc $common {flags} $inc -c input/closure_root.c -o "$od/closure_root.o"
t1=$(date +%s%N)
arm-none-eabi-nm -u "$od/wstr.o" | awk '{{print $NF}}' | sort -u > "$od/module.undefined"
arm-none-eabi-gcc -mcpu=cortex-m55 -mthumb -nostdlib -Wl,--gc-sections -Wl,-e,open_cfw_wstr_closure_root "$od/wstr.o" "$od/closure_root.o" -lgcc -o "$od/closure.elf"
t2=$(date +%s%N)
arm-none-eabi-nm -u "$od/closure.elf" | awk '{{print $NF}}' | sort -u > "$od/linked.undefined"
arm-none-eabi-nm -S --size-sort "$od/wstr.o" > "$od/wstr.nm"
for symbol in WStrReverseCpy WStrReverse WstrnCpy; do arm-none-eabi-objcopy --dump-section ".text.$symbol=$od/$symbol.bin" "$od/wstr.o"; done
for symbol in WStrReverseCpy WStrReverse; do arm-none-eabi-objdump -dr -j ".text.$symbol" "$od/wstr.o" > "$od/$symbol.disasm"; done
osha=$(sha256sum "$od/wstr.o" | awk '{{print $1}}'); rsha=$(sha256sum "$od/closure_root.o" | awk '{{print $1}}'); esha=$(sha256sum "$od/closure.elf" | awk '{{print $1}}'); mu=$(wc -l < "$od/module.undefined" | tr -d ' '); lu=$(wc -l < "$od/linked.undefined" | tr -d ' ')
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' '{lane}' '{config}' "$((t1-t0))" "$((t2-t1))" "$osha" "$rsha" "$esha" "$mu" "$lu" >> out/build-results.tsv
'''

started = time.time_ns()
subprocess.run(docker, input=script, text=True, check=True)
elapsed = time.time_ns()-started

stock_script = "set -eu\n"
for fn in functions:
    stock_script += f"arm-none-eabi-objdump -D -b binary -marm -Mforce-thumb --adjust-vma={fn['start']} stock/{fn['stock_name']}.bin > stock/{fn['stock_name']}.disasm\n"
subprocess.run(docker, input=stock_script, text=True, check=True)
norm = root/"input/normalize_disassembly.py"
for config in configs:
    lane = f"ambiq_exact__{config}"
    for fn in functions:
        name = fn["stock_name"]
        subprocess.run([sys.executable,str(norm),str(root/f"out/{lane}/{name}.disasm"),str(root/f"out/{lane}/{name}.norm")],check=True)
for fn in functions:
    name = fn["stock_name"]
    subprocess.run([sys.executable,str(norm),str(root/f"stock/{name}.disasm"),str(root/f"stock/{name}.norm")],check=True)

build = {row["lane"]:row for row in csv.DictReader(open(root/"out/build-results.tsv"), delimiter="\t")}
rows = []
for config in configs:
    lane = f"ambiq_exact__{config}"
    record = build[lane]
    for fn in functions:
        name = fn["stock_name"]
        candidate = root/f"out/{lane}/{name}.bin"; stock = root/f"stock/{name}.bin"
        candidate_norm = root/f"out/{lane}/{name}.norm"; stock_norm = root/f"stock/{name}.norm"
        cb, sb = candidate.read_bytes(), stock.read_bytes()
        rows.append({"lane":lane,"config":config,"function":name,"start":fn["start"],"end":fn["end"],"candidate_symbol":fn["candidate_symbol"],"evidence":fn["evidence"],"candidate_size":len(cb),"stock_size":len(sb),"size_delta":len(cb)-len(sb),"raw_match":"yes" if cb==sb else "no","strict_normalized_match":"yes" if candidate_norm.read_bytes()==stock_norm.read_bytes() else "no","candidate_sha256":sha(candidate),"stock_sha256":sha(stock),"candidate_normalized_sha256":sha(candidate_norm),"stock_normalized_sha256":sha(stock_norm),"compile_ns":record["compile_ns"],"link_ns":record["link_ns"],"object_sha256":record["object_sha256"],"linked_sha256":record["linked_sha256"]})
with open(root/"out/comparison-ledger.tsv","w",newline="") as f:
    writer=csv.DictWriter(f,list(rows[0]),delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows)
with open(root/"out/config-summary.tsv","w",newline="") as f:
    writer=csv.writer(f,delimiter="\t",lineterminator="\n");writer.writerow(("lane","config","functions","exact_size","aggregate_abs_size_delta","raw_matches","strict_normalized_matches"))
    for config in configs:
        lane=f"ambiq_exact__{config}"; selected=[row for row in rows if row["lane"]==lane]
        writer.writerow((lane,config,len(selected),sum(row["size_delta"]==0 for row in selected),sum(abs(row["size_delta"]) for row in selected),sum(row["raw_match"]=="yes" for row in selected),sum(row["strict_normalized_match"]=="yes" for row in selected)))
with open(root/"out/best-size-per-function.tsv","w",newline="") as f:
    writer=csv.writer(f,delimiter="\t",lineterminator="\n");writer.writerow(("function","stock_size","best_abs_delta","best_rows"))
    for fn in functions:
        selected=[row for row in rows if row["function"]==fn["stock_name"]]; best=min(abs(row["size_delta"]) for row in selected)
        writer.writerow((fn["stock_name"],selected[0]["stock_size"],best,",".join(f"{row['lane']}:{row['candidate_size']}({row['size_delta']:+d})" for row in selected if abs(row["size_delta"])==best)))
with open(root/"out/source-api-build-sizes.tsv","w",newline="") as f:
    writer=csv.writer(f,delimiter="\t",lineterminator="\n");writer.writerow(("lane","config","symbol","size","stock_bounded"))
    for config in configs:
        lane=f"ambiq_exact__{config}"
        for line in (root/f"out/{lane}/wstr.nm").read_text().splitlines():
            match=re.match(r"^[0-9a-f]+\s+([0-9a-f]+)\s+T\s+(WStr\S+|WstrnCpy)$",line)
            if match: writer.writerow((lane,config,match.group(2),int(match.group(1),16),"yes" if match.group(2) in {"WStrReverseCpy","WStrReverse"} else "no"))
(root/"out/matrix-timing.txt").write_text(f"matrix_elapsed_ns={elapsed}\n")
compiler=subprocess.check_output(docker[:-2]+["arm-none-eabi-gcc","--version"],text=True).splitlines()[0]
binutils=subprocess.check_output(docker[:-2]+["arm-none-eabi-objdump","--version"],text=True).splitlines()[0]
image=subprocess.check_output(["docker","image","inspect","--format","{{.Id}}","opencfw-arm-gcc:13.2-rel1"],text=True).strip()
(root/"out/toolchain.txt").write_text(f"container_tag=opencfw-arm-gcc:13.2-rel1\ncontainer_image_id={image}\ncompiler={compiler}\nbinutils={binutils}\n")
print("rows",len(rows),"elapsed_ns",elapsed,"raw",sum(row["raw_match"]=="yes" for row in rows),"normalized",sum(row["strict_normalized_match"]=="yes" for row in rows),"ledger_sha256",sha(root/"out/comparison-ledger.tsv"))

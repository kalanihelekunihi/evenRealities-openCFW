#!/usr/bin/env python3
import concurrent.futures
import csv
import hashlib
import os
import pathlib
import re
import subprocess
import sys
import time

root = pathlib.Path(sys.argv[1]).resolve()
source = root/"AmbiqSuite-R2.5.1/third_party/cordio/wsf/sources/port/freertos/wsf_efs.c"
wsf = root/"AmbiqSuite-R2.5.1/third_party/cordio/wsf"
firmware = (root/"stock-firmware.bin").read_bytes()

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

assert sha(source) == "878125a6bb701d0875d58c05bfcb4ad770c9f95f8c09f69706959795bee7741a"
assert hashlib.sha256(firmware).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

common = "-std=c11 -mcpu=cortex-m55 -mthumb -mno-unaligned-access -ffreestanding -fno-lto -fno-builtin -ffunction-sections -fdata-sections -fomit-frame-pointer -fno-unwind-tables -fno-asynchronous-unwind-tables -DWSF_ASSERT_ENABLED=0 -DWSF_TRACE_ENABLED=0 -DWSF_TOKEN_ENABLED=0 -DAM_DEBUG_PRINTF=1 -Wall -Wextra -Werror"
configs = {"O1":"-O1", "O3":"-O3", "Os_nosibling":"-Os -fno-optimize-sibling-calls"}

docker_base = ["docker", "run", "--rm", "-i", "--network", "none", "--read-only", "--security-opt", "label=disable", "--tmpfs", "/tmp:exec", "--user", f"{os.getuid()}:{os.getgid()}", "-w", "/work", "-e", "TMPDIR=/tmp", "-v", f"{root}:/work", "opencfw-arm-gcc:13.2-rel1", "sh", "-s"]

dependency_script = f'''set -eu
wsf=AmbiqSuite-R2.5.1/third_party/cordio/wsf
arm-none-eabi-gcc {common} -Ishim -I$wsf/sources/port/freertos -I$wsf/sources/util -I$wsf/include -M $wsf/sources/port/freertos/wsf_efs.c > out/wsf_efs.d
'''
subprocess.run(docker_base, input=dependency_script, text=True, check=True)

def build(item):
    config, flags = item
    script = f'''set -eu
wsf=AmbiqSuite-R2.5.1/third_party/cordio/wsf
inc="-Ishim -I$wsf/sources/port/freertos -I$wsf/sources/util -I$wsf/include"
od=out/{config}; mkdir -p "$od"
t0=$(date +%s%N)
arm-none-eabi-gcc {common} {flags} $inc -c $wsf/sources/port/freertos/wsf_efs.c -o "$od/wsf_efs.o"
arm-none-eabi-gcc {common} {flags} $inc -c input/closure_stubs.c -o "$od/closure_stubs.o"
t1=$(date +%s%N)
arm-none-eabi-nm -u "$od/wsf_efs.o" | awk '{{print $NF}}' | sort -u > "$od/module.undefined"
arm-none-eabi-gcc -mcpu=cortex-m55 -mthumb -nostdlib -Wl,--gc-sections -Wl,-e,open_cfw_wsf_efs_closure_root "$od/wsf_efs.o" "$od/closure_stubs.o" -lgcc -o "$od/closure.elf"
t2=$(date +%s%N)
arm-none-eabi-nm -u "$od/closure.elf" | awk '{{print $NF}}' | sort -u > "$od/linked.undefined"
arm-none-eabi-nm -S --size-sort "$od/wsf_efs.o" > "$od/wsf_efs.nm"
arm-none-eabi-objdump -dr "$od/wsf_efs.o" > "$od/wsf_efs.disasm"
arm-none-eabi-objdump -r "$od/wsf_efs.o" > "$od/wsf_efs.reloc"
for symbol in $(arm-none-eabi-nm -S "$od/wsf_efs.o" | awk '$3 ~ /^[Tt]$/ && $4 ~ /^WsfEfs/ {{print $4}}'); do
  arm-none-eabi-objcopy --dump-section ".text.$symbol=$od/$symbol.bin" "$od/wsf_efs.o"
done
printf '%s\t%s\t%s\n' {config} "$((t1-t0))" "$((t2-t1))" > "$od/timing.tsv"
'''
    started = time.time_ns()
    subprocess.run(docker_base, input=script, text=True, check=True)
    return config, time.time_ns()-started

wall_start = time.time_ns()
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    elapsed = dict(executor.map(build, configs.items()))
wall_elapsed = time.time_ns()-wall_start

rows = []
for config in configs:
    od = root/f"out/{config}"
    module_undefined = len(od.joinpath("module.undefined").read_text().splitlines())
    linked_undefined = len(od.joinpath("linked.undefined").read_text().splitlines())
    for path in sorted(od.glob("WsfEfs*.bin")):
        data = path.read_bytes()
        exact = []
        cursor = 0
        while data and (hit := firmware.find(data, cursor)) >= 0:
            exact.append(hit); cursor = hit+1
        rows.append({"config":config, "symbol":path.stem, "candidate_size":len(data), "candidate_sha256":sha(path), "raw_stock_hits":len(exact), "raw_stock_offsets":",".join(hex(x) for x in exact), "module_undefined":module_undefined, "linked_undefined":linked_undefined, "container_elapsed_ns":elapsed[config]})

with open(root/"out/compiled-symbol-census.tsv", "w", newline="") as f:
    writer = csv.DictWriter(f, list(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)

with open(root/"out/build-timing.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("config", "container_elapsed_ns", "compile_ns", "link_ns", "module_undefined", "linked_undefined"))
    for config in configs:
        compile_ns, link_ns = (root/f"out/{config}/timing.tsv").read_text().strip().split("\t")[1:]
        writer.writerow((config, elapsed[config], compile_ns, link_ns, len((root/f"out/{config}/module.undefined").read_text().splitlines()), len((root/f"out/{config}/linked.undefined").read_text().splitlines())))
(root/"out/wall-timing.txt").write_text(f"parallel_build_wall_ns={wall_elapsed}\n")
compiler = subprocess.check_output(docker_base[:-2] + ["arm-none-eabi-gcc", "--version"], text=True).splitlines()[0]
image = subprocess.check_output(["docker", "image", "inspect", "--format", "{{.Id}}", "opencfw-arm-gcc:13.2-rel1"], text=True).strip()
(root/"out/toolchain.txt").write_text(f"container_tag=opencfw-arm-gcc:13.2-rel1\ncontainer_image_id={image}\ncompiler={compiler}\n")
print("rows", len(rows), "raw_hits", sum(int(r["raw_stock_hits"]) for r in rows), "wall_ns", wall_elapsed, "ledger_sha256", sha(root/"out/compiled-symbol-census.tsv"))

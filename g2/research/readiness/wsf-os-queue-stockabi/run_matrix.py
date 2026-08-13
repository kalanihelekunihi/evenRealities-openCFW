#!/usr/bin/env python3
import csv, hashlib, os, pathlib, shutil, subprocess, sys, time

root = pathlib.Path(sys.argv[1]).resolve()
source_root = root / 'AmbiqSuite-R2.5.1/third_party/cordio/wsf'
expected = {
    'wsf_os.c': '892a7ae0283ba9274f80e48e6a2507cf49d3075fad7c3298656afc98a1a56e4a',
    'wsf_queue.c': '7dd109b4509d31c3222827b73f7ed5587e46a2c9d2de54ed8f30c599d418cf86',
}
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
for name, digest in expected.items():
    assert sha(source_root / f'sources/port/freertos/{name}') == digest
assert sha(root/'input/functions.tsv') == '63bca2329013c906c6e581dbdd88fd6cc466ee78975ba7676f5de61a047111b0'

configs = {
    'O0': '-O0',
    'O1': '-O1',
    'Og': '-Og',
    'Og_nosibling': '-Og -fno-optimize-sibling-calls',
    'O2': '-O2',
    'O2_noinline': '-O2 -fno-inline -fno-inline-functions -fno-inline-small-functions',
    'O3': '-O3',
    'O3_noinline': '-O3 -fno-inline -fno-inline-functions -fno-inline-small-functions',
    'Os': '-Os',
    'Os_noinline': '-Os -fno-inline -fno-inline-functions -fno-inline-small-functions',
    'Os_nosibling': '-Os -fno-optimize-sibling-calls',
    'Oz': '-Oz',
    'Oz_nosibling': '-Oz -fno-optimize-sibling-calls',
}
functions = list(csv.DictReader(open(root/'input/functions.tsv'), delimiter='\t'))

# Extract and authenticate stock spans before entering the compiler container.
firmware = (root/'stock-firmware.bin').read_bytes()
base = 0x00437fe0
(root/'stock').mkdir(exist_ok=True)
for fn in functions:
    start, end = int(fn['start'], 0), int(fn['end'], 0)
    (root/f"stock/{fn['stock_name']}.bin").write_bytes(firmware[start-base:end-base])

common = '-std=c11 -mcpu=cortex-m55 -mthumb -mno-unaligned-access -ffreestanding -fno-lto -fno-builtin -ffunction-sections -fdata-sections -fomit-frame-pointer -fno-unwind-tables -fno-asynchronous-unwind-tables -DWSF_MAX_HANDLERS=10 -Wall -Wextra -Werror'
script = f'''set -eu
wsf=AmbiqSuite-R2.5.1/third_party/cordio/wsf
inc="-Ishim -I$wsf/sources/port/freertos -I$wsf/include"
common="{common}"
mkdir -p out/deps
t0=$(date +%s%N)
arm-none-eabi-gcc $common $inc -M "$wsf/sources/port/freertos/wsf_os.c" > out/deps/wsf_os.d
arm-none-eabi-gcc $common $inc -M "$wsf/sources/port/freertos/wsf_queue.c" > out/deps/wsf_queue.d
t1=$(date +%s%N)
printf 'dependency_scan_ns=%s\n' "$((t1-t0))" > out/dependency-timing.txt
printf 'config\tcompile_ns\tlink_ns\tos_object_sha256\tqueue_object_sha256\tstubs_object_sha256\tlinked_sha256\tos_undefined\tqueue_undefined\tcombined_undefined\tlinked_undefined\n' > out/build-results.tsv
'''
for config, flags in configs.items():
    script += f'''od=out/{config}; mkdir -p "$od"
t0=$(date +%s%N)
arm-none-eabi-gcc $common {flags} $inc -c "$wsf/sources/port/freertos/wsf_os.c" -o "$od/wsf_os.o" 2>"$od/wsf_os.stderr"
arm-none-eabi-gcc $common {flags} $inc -c "$wsf/sources/port/freertos/wsf_queue.c" -o "$od/wsf_queue.o" 2>"$od/wsf_queue.stderr"
arm-none-eabi-gcc $common {flags} $inc -c input/closure_stubs.c -o "$od/closure_stubs.o" 2>"$od/closure_stubs.stderr"
t1=$(date +%s%N)
arm-none-eabi-nm -u "$od/wsf_os.o" | awk '{{print $NF}}' | sort -u > "$od/wsf_os.undefined"
arm-none-eabi-nm -u "$od/wsf_queue.o" | awk '{{print $NF}}' | sort -u > "$od/wsf_queue.undefined"
arm-none-eabi-ld -r "$od/wsf_os.o" "$od/wsf_queue.o" -o "$od/modules.rel.o"
arm-none-eabi-nm -u "$od/modules.rel.o" | awk '{{print $NF}}' | sort -u > "$od/combined.undefined"
arm-none-eabi-gcc -mcpu=cortex-m55 -mthumb -nostdlib -Wl,--gc-sections -Wl,-e,open_cfw_wsf_stockabi_closure_root "$od/wsf_os.o" "$od/wsf_queue.o" "$od/closure_stubs.o" -lgcc -o "$od/closure.elf"
t2=$(date +%s%N)
arm-none-eabi-nm -u "$od/closure.elf" | awk '{{print $NF}}' | sort -u > "$od/linked.undefined"
arm-none-eabi-nm -S --size-sort "$od/wsf_os.o" > "$od/wsf_os.nm"
arm-none-eabi-nm -S --size-sort "$od/wsf_queue.o" > "$od/wsf_queue.nm"
arm-none-eabi-objdump -dr "$od/wsf_os.o" > "$od/wsf_os.disasm"
arm-none-eabi-objdump -dr "$od/wsf_queue.o" > "$od/wsf_queue.disasm"
tail -n +2 input/functions.tsv | while read -r unit stock start end symbol; do
 arm-none-eabi-objcopy --dump-section ".text.$symbol=$od/$stock.bin" "$od/$unit.o"
 arm-none-eabi-objdump -dr -j ".text.$symbol" "$od/$unit.o" > "$od/$stock.disasm"
done
ossha=$(sha256sum "$od/wsf_os.o" | awk '{{print $1}}'); qsha=$(sha256sum "$od/wsf_queue.o" | awk '{{print $1}}'); ssha=$(sha256sum "$od/closure_stubs.o" | awk '{{print $1}}'); esha=$(sha256sum "$od/closure.elf" | awk '{{print $1}}')
uo=$(wc -l < "$od/wsf_os.undefined" | tr -d ' '); uq=$(wc -l < "$od/wsf_queue.undefined" | tr -d ' '); uc=$(wc -l < "$od/combined.undefined" | tr -d ' '); ul=$(wc -l < "$od/linked.undefined" | tr -d ' ')
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' '{config}' "$((t1-t0))" "$((t2-t1))" "$ossha" "$qsha" "$ssha" "$esha" "$uo" "$uq" "$uc" "$ul" >> out/build-results.tsv
'''

docker = ['docker','run','--rm','-i','--network','none','--read-only','--security-opt','label=disable','--tmpfs','/tmp:exec','--user',f'{os.getuid()}:{os.getgid()}','-w','/work','-e','TMPDIR=/tmp','-v',f'{root}:/work','opencfw-arm-gcc:13.2-rel1','sh','-s']
t0=time.time_ns()
subprocess.run(docker, input=script, text=True, check=True)
matrix_elapsed=time.time_ns()-t0

# Stock disassembly is produced by the same pinned objdump; normalization is
# host-side because the minimal compiler image intentionally excludes Python.
stock_script='set -eu\n'
for fn in functions:
    stock_script += f"arm-none-eabi-objdump -D -b binary -marm -Mforce-thumb --adjust-vma={fn['start']} stock/{fn['stock_name']}.bin > stock/{fn['stock_name']}.disasm\n"
subprocess.run(docker[:-2]+['sh','-s'], input=stock_script, text=True, check=True)
normalizer=root/'input/normalize_disassembly.py'
for config in configs:
    for fn in functions:
        name=fn['stock_name']
        subprocess.run([sys.executable,str(normalizer),str(root/f'out/{config}/{name}.disasm'),str(root/f'out/{config}/{name}.norm')],check=True)
for fn in functions:
    name=fn['stock_name']
    subprocess.run([sys.executable,str(normalizer),str(root/f'stock/{name}.disasm'),str(root/f'stock/{name}.norm')],check=True)

build_rows={r['config']:r for r in csv.DictReader(open(root/'out/build-results.tsv'),delimiter='\t')}
comparison=[]
for config in configs:
    for fn in functions:
        name=fn['stock_name']; candidate=root/f'out/{config}/{name}.bin'; stock=root/f'stock/{name}.bin'; cn=root/f'out/{config}/{name}.norm'; sn=root/f'stock/{name}.norm'
        cb, sb = candidate.read_bytes(), stock.read_bytes()
        comparison.append({'config':config,'unit':fn['unit'],'function':name,'start':fn['start'],'end':fn['end'],'candidate_symbol':fn['candidate_symbol'],'candidate_size':len(cb),'stock_size':len(sb),'size_delta':len(cb)-len(sb),'raw_match':'yes' if cb==sb else 'no','strict_normalized_match':'yes' if cn.read_bytes()==sn.read_bytes() else 'no','candidate_sha256':sha(candidate),'stock_sha256':sha(stock),'candidate_normalized_sha256':sha(cn),'stock_normalized_sha256':sha(sn),'compile_ns':build_rows[config]['compile_ns'],'link_ns':build_rows[config]['link_ns'],'os_object_sha256':build_rows[config]['os_object_sha256'],'queue_object_sha256':build_rows[config]['queue_object_sha256'],'linked_sha256':build_rows[config]['linked_sha256']})
fields=list(comparison[0])
with open(root/'out/comparison-ledger.tsv','w',newline='') as f:
    w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(comparison)

with open(root/'out/config-summary.tsv','w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n'); w.writerow(('config','functions','os_functions','queue_functions','exact_size','os_exact_size','queue_exact_size','aggregate_abs_size_delta','os_abs_size_delta','queue_abs_size_delta','raw_matches','strict_normalized_matches'))
    for config in configs:
        rs=[r for r in comparison if r['config']==config]; ors=[r for r in rs if r['unit']=='wsf_os']; qrs=[r for r in rs if r['unit']=='wsf_queue']
        w.writerow((config,len(rs),len(ors),len(qrs),sum(r['size_delta']==0 for r in rs),sum(r['size_delta']==0 for r in ors),sum(r['size_delta']==0 for r in qrs),sum(abs(r['size_delta']) for r in rs),sum(abs(r['size_delta']) for r in ors),sum(abs(r['size_delta']) for r in qrs),sum(r['raw_match']=='yes' for r in rs),sum(r['strict_normalized_match']=='yes' for r in rs)))
with open(root/'out/best-size-per-function.tsv','w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(('unit','function','stock_size','best_abs_delta','best_rows'))
    for fn in functions:
        rs=[r for r in comparison if r['function']==fn['stock_name']]; best=min(abs(r['size_delta']) for r in rs); picks=','.join(f"{r['config']}:{r['candidate_size']}({r['size_delta']:+d})" for r in rs if abs(r['size_delta'])==best)
        w.writerow((fn['unit'],fn['stock_name'],rs[0]['stock_size'],best,picks))
(root/'out/matrix-timing.txt').write_text(f'matrix_elapsed_ns={matrix_elapsed}\n')
print('root',root,'rows',len(comparison),'elapsed_ns',matrix_elapsed,'raw',sum(r['raw_match']=='yes' for r in comparison),'normalized',sum(r['strict_normalized_match']=='yes' for r in comparison),'ledger_sha256',sha(root/'out/comparison-ledger.tsv'))

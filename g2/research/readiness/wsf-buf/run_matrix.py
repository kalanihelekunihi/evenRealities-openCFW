#!/usr/bin/env python3
import csv, hashlib, os, pathlib, subprocess, sys, time

root=pathlib.Path(sys.argv[1]).resolve(); wsf=root/'AmbiqSuite-R2.5.1/third_party/cordio/wsf'
sha=lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert sha(wsf/'sources/port/freertos/wsf_buf.c')=='e13de1419b29d0d82eee31ce1fe7d4c776eba98bf83b04001842f8cba7027a08'
functions=list(csv.DictReader(open(root/'input/functions.tsv'),delimiter='\t'))
configs={'O0':'-O0','O1':'-O1','Og':'-Og','Og_nosibling':'-Og -fno-optimize-sibling-calls','O2':'-O2','O2_noinline':'-O2 -fno-inline -fno-inline-functions -fno-inline-small-functions','O3':'-O3','O3_noinline':'-O3 -fno-inline -fno-inline-functions -fno-inline-small-functions','Os':'-Os','Os_noinline':'-Os -fno-inline -fno-inline-functions -fno-inline-small-functions','Os_nosibling':'-Os -fno-optimize-sibling-calls','Oz':'-Oz','Oz_nosibling':'-Oz -fno-optimize-sibling-calls'}
variants={'archive_notrace':'','stock_warn_seam':'-include shim/wsf_buf_trace_override.h'}

firmware=(root/'stock-firmware.bin').read_bytes(); base=0x437fe0
for fn in functions:
    s,e=int(fn['start'],0),int(fn['end'],0); (root/f"stock/{fn['stock_name']}.bin").write_bytes(firmware[s-base:e-base])

common='-std=c11 -mcpu=cortex-m55 -mthumb -mno-unaligned-access -ffreestanding -fno-lto -fno-builtin -ffunction-sections -fdata-sections -fomit-frame-pointer -fno-unwind-tables -fno-asynchronous-unwind-tables -DWSF_BUF_FREE_CHECK=1 -DWSF_BUF_ALLOC_BEST_FIT_FAIL_ASSERT=0 -DWSF_BUF_ALLOC_FAIL_ASSERT=1 -DWSF_BUF_STATS=0 -DWSF_BUF_STATS_HIST=0 -DWSF_OS_DIAG=0 -DWSF_ASSERT_ENABLED=0 -Wall -Wextra -Werror -Wno-unused-parameter'
script=f'''set -eu
wsf=AmbiqSuite-R2.5.1/third_party/cordio/wsf
inc="-I$wsf/sources/port/freertos -I$wsf/include -Ishim"
common="{common}"
mkdir -p out/deps
printf 'lane\tvariant\tconfig\tcompile_ns\tlink_ns\tobject_sha256\tstubs_sha256\tlinked_sha256\tmodule_undefined\tlinked_undefined\n' > out/build-results.tsv
'''
for variant,vflags in variants.items():
    script+=f'''t0=$(date +%s%N); arm-none-eabi-gcc $common {vflags} $inc -M "$wsf/sources/port/freertos/wsf_buf.c" > out/deps/{variant}.d; t1=$(date +%s%N); printf '{variant}_dependency_ns=%s\n' "$((t1-t0))" >> out/dependency-timing.txt
'''
    for config,cflags in configs.items():
        lane=f'{variant}__{config}'
        script+=f'''od=out/{lane}; mkdir -p "$od"
t0=$(date +%s%N)
arm-none-eabi-gcc $common {vflags} {cflags} $inc -c "$wsf/sources/port/freertos/wsf_buf.c" -o "$od/wsf_buf.o" 2>"$od/wsf_buf.stderr"
arm-none-eabi-gcc $common {vflags} {cflags} $inc -c input/closure_stubs.c -o "$od/closure_stubs.o" 2>"$od/closure_stubs.stderr"
t1=$(date +%s%N)
arm-none-eabi-nm -u "$od/wsf_buf.o" | awk '{{print $NF}}' | sort -u > "$od/module.undefined"
arm-none-eabi-gcc -mcpu=cortex-m55 -mthumb -nostdlib -Wl,--gc-sections -Wl,-e,open_cfw_wsf_buf_closure_root "$od/wsf_buf.o" "$od/closure_stubs.o" -lgcc -o "$od/closure.elf"
t2=$(date +%s%N)
arm-none-eabi-nm -u "$od/closure.elf" | awk '{{print $NF}}' | sort -u > "$od/linked.undefined"
arm-none-eabi-nm -S --size-sort "$od/wsf_buf.o" > "$od/wsf_buf.nm"
arm-none-eabi-objdump -dr "$od/wsf_buf.o" > "$od/wsf_buf.disasm"
tail -n +2 input/functions.tsv | while read -r stock start end symbol evidence; do
 arm-none-eabi-objcopy --dump-section ".text.$symbol=$od/$stock.bin" "$od/wsf_buf.o"
 arm-none-eabi-objdump -dr -j ".text.$symbol" "$od/wsf_buf.o" > "$od/$stock.disasm"
done
osha=$(sha256sum "$od/wsf_buf.o" | awk '{{print $1}}'); ssha=$(sha256sum "$od/closure_stubs.o" | awk '{{print $1}}'); esha=$(sha256sum "$od/closure.elf" | awk '{{print $1}}'); um=$(wc -l < "$od/module.undefined" | tr -d ' '); ul=$(wc -l < "$od/linked.undefined" | tr -d ' ')
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' '{lane}' '{variant}' '{config}' "$((t1-t0))" "$((t2-t1))" "$osha" "$ssha" "$esha" "$um" "$ul" >> out/build-results.tsv
'''
docker=['docker','run','--rm','-i','--network','none','--read-only','--security-opt','label=disable','--tmpfs','/tmp:exec','--user',f'{os.getuid()}:{os.getgid()}','-w','/work','-e','TMPDIR=/tmp','-v',f'{root}:/work','opencfw-arm-gcc:13.2-rel1','sh','-s']
t0=time.time_ns();subprocess.run(docker,input=script,text=True,check=True);elapsed=time.time_ns()-t0

stock_script='set -eu\n'
for fn in functions:stock_script+=f"arm-none-eabi-objdump -D -b binary -marm -Mforce-thumb --adjust-vma={fn['start']} stock/{fn['stock_name']}.bin > stock/{fn['stock_name']}.disasm\n"
subprocess.run(docker,input=stock_script,text=True,check=True)
norm=root/'input/normalize_disassembly.py'
for variant in variants:
 for config in configs:
  lane=f'{variant}__{config}'
  for fn in functions:
   name=fn['stock_name'];subprocess.run([sys.executable,str(norm),str(root/f'out/{lane}/{name}.disasm'),str(root/f'out/{lane}/{name}.norm')],check=True)
for fn in functions:
 name=fn['stock_name'];subprocess.run([sys.executable,str(norm),str(root/f'stock/{name}.disasm'),str(root/f'stock/{name}.norm')],check=True)

build={r['lane']:r for r in csv.DictReader(open(root/'out/build-results.tsv'),delimiter='\t')}; rows=[]
for variant in variants:
 for config in configs:
  lane=f'{variant}__{config}';b=build[lane]
  for fn in functions:
   name=fn['stock_name'];cp=root/f'out/{lane}/{name}.bin';sp=root/f'stock/{name}.bin';cn=root/f'out/{lane}/{name}.norm';sn=root/f'stock/{name}.norm';cb=cp.read_bytes();sb=sp.read_bytes()
   rows.append({'lane':lane,'variant':variant,'config':config,'function':name,'start':fn['start'],'end':fn['end'],'candidate_symbol':fn['candidate_symbol'],'evidence':fn['evidence'],'candidate_size':len(cb),'stock_size':len(sb),'size_delta':len(cb)-len(sb),'raw_match':'yes' if cb==sb else 'no','strict_normalized_match':'yes' if cn.read_bytes()==sn.read_bytes() else 'no','candidate_sha256':sha(cp),'stock_sha256':sha(sp),'candidate_normalized_sha256':sha(cn),'stock_normalized_sha256':sha(sn),'compile_ns':b['compile_ns'],'link_ns':b['link_ns'],'object_sha256':b['object_sha256'],'linked_sha256':b['linked_sha256']})
with open(root/'out/comparison-ledger.tsv','w',newline='') as f:w=csv.DictWriter(f,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
with open(root/'out/config-summary.tsv','w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(('lane','variant','config','functions','exact_size','aggregate_abs_size_delta','raw_matches','strict_normalized_matches'))
 for variant in variants:
  for config in configs:
   lane=f'{variant}__{config}';rs=[r for r in rows if r['lane']==lane];w.writerow((lane,variant,config,len(rs),sum(r['size_delta']==0 for r in rs),sum(abs(r['size_delta']) for r in rs),sum(r['raw_match']=='yes' for r in rs),sum(r['strict_normalized_match']=='yes' for r in rs)))
with open(root/'out/best-size-per-function.tsv','w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(('function','stock_size','best_abs_delta','best_rows'))
 for fn in functions:
  rs=[r for r in rows if r['function']==fn['stock_name']];best=min(abs(r['size_delta']) for r in rs);picks=','.join(f"{r['lane']}:{r['candidate_size']}({r['size_delta']:+d})" for r in rs if abs(r['size_delta'])==best);w.writerow((fn['stock_name'],rs[0]['stock_size'],best,picks))
(root/'out/matrix-timing.txt').write_text(f'matrix_elapsed_ns={elapsed}\n')
print('root',root,'rows',len(rows),'elapsed_ns',elapsed,'raw',sum(r['raw_match']=='yes' for r in rows),'normalized',sum(r['strict_normalized_match']=='yes' for r in rows),'ledger_sha256',sha(root/'out/comparison-ledger.tsv'))

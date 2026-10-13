#!/usr/bin/env python3
"""Isolated CASE GCC source-size experiment; no flashing or source admission."""
from pathlib import Path
import hashlib,json,shlex,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected=ROOT/'g2/analysis/component-goal-20261013/case-wave002-call-contracts/command-evidence/receipt.json';sel=json.loads(selected.read_text());sources=[ROOT/x['source'] for x in sel['sources']]+sorted((ROOT/'g2/components/case/startup_candidate_20261011').glob('*.c'))+[HERE/'compiler_memory.c']
assert len(sources)==len(set(sources))
for row in sel['sources']:assert sha(ROOT/row['source'])==row['sha256'],row['source']
roots_path=ROOT/'g2/analysis/c-source-completion-20261011/m0/case_semantic_corrected_optimized.indirect-roots.json';roots=json.loads(roots_path.read_text());root_names=sorted(set(x['source_symbol'] for x in roots['rows']));assert len(roots['rows'])==39
acq=json.loads((ROOT/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text())[0];tool=(ROOT/'g2/analysis/touch-compiler14-successor-2026-10-09'/acq['gcc']).parents[1];assert sha(tool/'bin/arm-none-eabi-gcc')==acq['gcc_sha256']
layout=ROOT/'g2/analysis/c-source-completion-20261011/m0/case_reset_placement_probe.ld'
# The early hook is a real local symbol, not an undefined global linker root.
# Retain its authored section and avoid creating a same-name global import.
(HERE/'layout.ld').write_text(layout.read_text().replace('.text : {','.text : { KEEP(*(.text.case_early_hook_84ae))'))
force_roots=[n for n in root_names if n!='case_early_hook_84ae']+['case_vformat','case_crt_init_known_defaults','memcpy','memset']
oldpath=HERE/'build-receipt.json';old=json.loads(oldpath.read_text()) if oldpath.exists() else {}
cache={x['source']:x for x in old.get('sources',[])}
objects=[];commands=[];records=[]
for i,p in enumerate(sources):
 out=f'/out/{i:03d}-{p.stem}.o';src='/repo/'+str(p.relative_to(ROOT));lto='__asm' not in p.read_text();flags=['-mcpu=cortex-m0plus','-mthumb','-mfloat-abi=soft','-std=c11','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-merge-constants','-fno-ipa-icf','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra']+(['-flto'] if lto else [])
 if not lto:flags.append('-masm-syntax-unified')
 if p.name=='compiler_memory.c':flags.append('-fno-tree-loop-distribute-patterns')
 cmd=['/tool/bin/arm-none-eabi-gcc',*flags,'-MD','-MF',out+'.d','-c',src,'-o',out]
 oldrow=cache.get(str(p.relative_to(ROOT)),{});target=HERE/Path(out).name
 reusable=oldrow.get('command')==cmd and oldrow.get('source_sha256')==sha(p) and target.exists() and oldrow.get('object_sha256')==sha(target) and all(sha(ROOT/k)==h for k,h in oldrow.get('repository_dependencies',{}).items())
 if not reusable:commands.append(shlex.join(cmd))
 objects.append(out);records.append({'source':str(p.relative_to(ROOT)),'source_sha256':sha(p),'LTO':lto,'command':cmd,'object':str(target.relative_to(ROOT)),'reused_verified_object':reusable})
runtime=ROOT/'g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/gcc-arm14-runtime/libgcc/config/arm/lib1funcs.S'
runtime_cmd=['/tool/bin/arm-none-eabi-gcc','-mcpu=cortex-m0plus','-mthumb',*['-DL_thumb1_case_'+n for n in ['sqi','uqi','shi','uhi']],'-c','/repo/'+str(runtime.relative_to(ROOT)),'-o','/out/compiler_switches.o']
commands.append(shlex.join(runtime_cmd));objects.append('/out/compiler_switches.o')
link=['/tool/bin/arm-none-eabi-gcc','-mcpu=cortex-m0plus','-mthumb','-Oz','-flto=6','-fno-ipa-icf','-nostdlib','-Wl,-T,/out/layout.ld,--gc-sections,-Map,/out/case.map',*['-Wl,-u,'+n for n in force_roots],*objects,'-o','/out/case.elf']
parallel=['set -eu',"pids=''"]
for i,cmd in enumerate(commands):
 parallel += [cmd+' &', 'pids="$pids $!"']
 if i%6==5 or i==len(commands)-1:
  parallel += ['for job in $pids; do wait "$job"; done',"pids=''"]
parallel.append(shlex.join(link));(HERE/'compile.sh').write_text('\n'.join(parallel)+'\n')
base=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',str(ROOT)+':/repo:ro','-v',str(tool)+':/tool:ro','-v',str(HERE)+':/out:rw','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/bin/sh','/out/compile.sh']
result=subprocess.run(base,capture_output=True,text=True);(HERE/'build.log').write_text(result.stdout+result.stderr)
for row in records:
 assert sha(ROOT/row['source'])==row['source_sha256']
 p=ROOT/row['object'];row['object_sha256']=sha(p) if p.exists() else None
 dep=Path(str(p)+'.d')
 if dep.exists():
  deps=dep.read_text().replace('\\\n',' ').split(':',1)[1].split();row['repository_dependencies']={x[6:]:sha(ROOT/x[6:]) for x in deps if x.startswith('/repo/')}
r={'status':'SOURCE_SIZE_BUILD_COMPLETED' if result.returncode==0 else 'SOURCE_SIZE_BUILD_FAILED','returncode':result.returncode,'sources':records,'link_command':link,'roots':root_names,'roots_evidence_sha256':sha(roots_path),'compiler_sha256':acq['gcc_sha256'],'selected_manifest_sha256':sha(selected),'layout_sha256':sha(HERE/'layout.ld'),'build_log_sha256':sha(HERE/'build.log'),'limits':['Experimental optimization profile only; no native byte equality, final scatter or hardware claim.','Known39 aligned callback roots retained; complete computed/indirect reachability remains unproven.','Inline-assembly source units excluded from LTO to retain native ABI symbol references.']}
if result.returncode==0:r['elf_sha256']=sha(HERE/'case.elf')
r['runtime_provider']={'source':str(runtime.relative_to(ROOT)),'sha256':sha(runtime),'command':runtime_cmd,'object_sha256':sha(HERE/'compiler_switches.o') if (HERE/'compiler_switches.o').exists() else None,'license':'GPL-3.0-or-later WITH GCC-exception-3.1'}
(HERE/'build-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],result.returncode);print((result.stdout+result.stderr)[-4000:])

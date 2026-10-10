#!/usr/bin/env python3
"""Build a non-flashable Cortex-M0+ CASE source candidate from existing bounded sources."""
from pathlib import Path
import subprocess, json, hashlib, shlex, sys
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
REPORT=ROOT/'g2/analysis/case-source-candidate-round2-20261010'
SOURCES=[
 'source_candidate_20261010/evidenced_providers.c', 'binary_forward_offline/forward.c','deferred_consumer_offline/consumer.c',
 'deferred_event_offline/deferred.c','event_flags_offline/events.c',
 'event_waiters_offline/waiters.c','frame_callback_offline/frame.c',
 'frame_dispatch_offline/dispatch.c','local_commands_offline/local.c',
 'uart_error_atomic_offline/uart.c','uart_receive_offline/receive.c',
 'uart_start_offline/start.c']
CLANG='/usr/bin/clang'; AR='/opt/homebrew/bin/arm-none-eabi-ar'; NM='/opt/homebrew/bin/arm-none-eabi-nm'
FLAGS=['--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-mfloat-abi=soft','-std=c11','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-Wall','-Wextra']
OUT=HERE/'build'; OUT.mkdir(exist_ok=True)
receipts=[]; objects=[]
for rel in SOURCES:
 src=HERE.parent/rel; obj=OUT/(rel.replace('/','__')+'.o')
 dep=OUT/(rel.replace('/','__')+'.d')
 cmd=[CLANG,*FLAGS,'-MD','-MF',str(dep),'-c',str(src),'-o',str(obj)]
 run=subprocess.run(cmd,text=True,capture_output=True)
 deps=dep.read_text().replace('\\\n',' ').split(':',1)[1].split() if run.returncode==0 else []
 receipts.append({'source':str(src.relative_to(ROOT)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'command':shlex.join(cmd),'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'dependencies':[{'path':str(Path(d).resolve().relative_to(ROOT)) if Path(d).resolve().is_relative_to(ROOT) else str(Path(d).resolve()),'sha256':hashlib.sha256(Path(d).read_bytes()).hexdigest()} for d in deps]})
 if run.returncode: raise SystemExit(json.dumps(receipts[-1],indent=2))
 objects.append(obj)
archive=OUT/'libcase_source_candidate.a'
archive.unlink(missing_ok=True)
cmd=[AR,'rcsD',str(archive),*[str(x) for x in objects]]
run=subprocess.run(cmd,text=True,capture_output=True)
if run.returncode: raise SystemExit(run.stderr)
first_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
archive.unlink()
rebuild=subprocess.run(cmd,text=True,capture_output=True)
if rebuild.returncode: raise SystemExit(rebuild.stderr)
second_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
if first_hash!=second_hash: raise SystemExit('nondeterministic archive rebuild')
cmdnm=[NM,'-A',*[str(x) for x in objects]]
nm=subprocess.run(cmdnm,text=True,capture_output=True,check=True).stdout
(REPORT/'nm.txt').write_text(nm)
provides=set(); needs=set()
for line in nm.splitlines():
 parts=line.split()
 if len(parts)<3: continue
 typ,sym=parts[-2:]
 if typ=='U': needs.add(sym)
 elif typ.upper() in ('T','D','B','R','C','W'): provides.add(sym)
receipt={'target':'arm-none-eabi cortex-m0plus thumb soft float','python_interpreter':sys.executable,'python_version':sys.version.split()[0],'tool_versions':{x:subprocess.run([v,'--version'],capture_output=True,text=True).stdout.splitlines()[0] for x,v in [('clang',CLANG),('ar',AR),('nm',NM)]},'tool_sha256':{x:hashlib.sha256(Path(v).read_bytes()).hexdigest() for x,v in [('clang',CLANG),('ar',AR),('nm',NM)]},'flags':FLAGS,'sources':receipts,'archive':str(archive.relative_to(ROOT)),'archive_sha256':second_hash,'archive_rebuild_same_sha256':first_hash==second_hash,'archive_command':shlex.join(cmd),'nm_command':shlex.join(cmdnm),'provided_symbols':sorted(provides),'unresolved_symbols':sorted(needs-provides),'source_count':len(SOURCES),'object_count':len(objects)}
(REPORT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'source_count':len(SOURCES),'provided':len(provides),'unresolved':receipt['unresolved_symbols']},indent=2))

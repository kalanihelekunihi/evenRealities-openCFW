#!/usr/bin/env python3
"""Compile the actual pinned Nordic port with its recovered critical assertions."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-critical';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
 original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/port_cmsis.c'));source=ROOT/row['source'];assert sha(source)==row['source_sha256']
 command=row['command'];flags=command[1:command.index('-c')];obj=out/'native_port_cmsis.o';dep=out/'native_port_cmsis.d';header=ROOT/'r1/source-config/rtos/native_port_assert.h'
 cmd=['clang',*flags,'-fshort-enums','-fno-delete-null-pointer-checks','-include',str(header),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
 inputs={str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else p:sha(Path(p)) for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split()}
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for path,digest in inputs.items():
   if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
 undefined,defined=undefined_symbols(obj);unit=dict(source=row['source'],source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
 selected=out/'critical-only.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=vPortEnterCritical','--undefined=vPortExitCritical',str(obj),'-o',str(selected)],check=True);remaining,_=undefined_symbols(selected);assert not remaining,remaining
 (out/'report.json').write_text(json.dumps(dict(units=[unit],inputs=inputs,selected_object_sha256=sha(selected),remaining_symbols=remaining,scope='Actual source-compiled Nordic critical functions; linker selects only those functions/state to avoid scheduler-start requirements',limitations=['Whole scheduler integration and assertions in other port functions remain separately gated.','Original instruction identity and physical exception behavior remain unproven.']),indent=2)+'\n');print('Actual port critical functions compiled with native assertions; no unresolved references')
if __name__=='__main__':main()

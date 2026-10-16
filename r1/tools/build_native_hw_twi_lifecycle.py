#!/usr/bin/env python3
"""Compile build-only native hardware TWI lifecycle."""
import hashlib,json,subprocess
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-hw-twi-lifecycle';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
 source=ROOT/'r1/components/board/native_hw_twi_lifecycle.c';obj=out/'native_hw_twi_lifecycle.o';dep=out/'native_hw_twi_lifecycle.d'
 parent=json.loads((BASE/'software-twi/gpio-report.json').read_text());cmd=parent['units'][0]['command'][:]+['-I'+str(ROOT/'r1/reconstructed')]
 cmd.insert(1,'-I'+str(ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/integration/nrfx/legacy'));cmd[cmd.index('-MF')+1]=str(dep);cmd[cmd.index('-c')+1]=str(source);cmd[cmd.index('-o')+1]=str(obj);subprocess.run(cmd,check=True)
 undefined,defined=undefined_symbols(obj);row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
 inputs={str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else p:sha(Path(p)) for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split()}
 import zipfile
 sdk=ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560';archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as z:
  for p,h in inputs.items():
   path=ROOT/p
   if path.is_relative_to(sdk):assert hashlib.sha256(z.read(str(path.relative_to(sdk.parent)))).hexdigest()==h,p
 (out/'report.json').write_text(json.dumps(dict(units=[row],inputs=inputs,application_linked=False,instruction_identity=False),indent=2)+'\n');print('Native hardware TWI lifecycle compiled; remaining:',', '.join(undefined))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Compile recovered RTT locking/initialization wrapper over pinned SEGGER source."""
import hashlib,json,subprocess
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-rtt-write';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
 source=ROOT/'r1/components/runtime/native_rtt_write.c';obj=out/'native_rtt_write.o';dep=out/'native_rtt_write.d'
 sdk_report=BASE/'sdk-segger-rtt/report.json';sdk=json.loads(sdk_report.read_text());template=sdk['configuration_command'];flags=template[1:template.index('-MD')]
 cmd=['clang',*flags,'-Os','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
 undefined,defined=undefined_symbols(obj);row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
 inputs={str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else p:sha(Path(p)) for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split()}
 for path,digest in inputs.items():
  if path.startswith('vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'):assert sdk['inputs'].get(path)==digest,path
 inputs[str(sdk_report.relative_to(ROOT))]=sha(sdk_report)
 (out/'report.json').write_text(json.dumps(dict(units=[row],inputs=inputs,application_linked=False,instruction_identity=False),indent=2)+'\n');print('Native RTT write wrapper compiled; remaining:',', '.join(undefined))
if __name__=='__main__':main()

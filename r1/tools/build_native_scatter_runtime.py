#!/usr/bin/env python3
"""Link source scatter startup; leave application entry explicitly unresolved."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'native-scatter-runtime';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);objects=[];providers={};inputs={str(Path(__file__).resolve().relative_to(ROOT)):sha(Path(__file__))}
    for directory,name in [('native-scatter-dispatch','native_scatter_dispatch.o'),('native-scatter-data','native_scatter_data.o')]:
        rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r.get('relocatable_sha256') or r['units'][0]['object_sha256'])
        providers[str(rp.relative_to(BASE))]=sha(rp)
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path;inputs[path]=digest
        objects.append(obj)
    linked=out/'native-scatter-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);unresolved,defined=undefined_symbols(linked);assert unresolved==['r1_native_application_entry'],unresolved
    report=dict(status='candidate-native-scatter-application-unresolved',provider_reports=providers,objects={str(p.relative_to(BASE)):sha(p) for p in objects},inputs=inputs,linked_sha256=sha(linked),undefined_symbols=unresolved,defined_symbols=defined,original_instruction_identity=False,application_linked=False,gates=['Scatter dispatch, runtime handoff, source handler configuration and initialization providers compile and link; r1_native_application_entry remains explicitly unresolved. The verification application boundary is not an executable fallback. Raw handoff registers/LR, source-owned initialization data and whole-image integration remain unproven.','Bounded native behavior checks, complete native ABI and original instruction/whole-image identity remain distinct.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Native scatter runtime: application entry unresolved')
if __name__=='__main__':main()

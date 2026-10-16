#!/usr/bin/env python3
"""Integrate reset decoder source, leaving retained diagnostic providers explicit."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-reset-decoder-runtime';out.mkdir(exist_ok=True);reports={};objects=[];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-reset-decoder','native_reset_decoder.o'),('native-gxt310-mode-runtime','native-gxt310-mode-runtime.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);reports[str(rp.relative_to(BASE))]=sha(rp);objects.append(obj)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-reset-decoder-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert 'r1_reset_reason_decode_and_report' not in u and {'r1_reset_trace_byte_read','r1_reset_trace_program_counter_read','r1_reset_trace_return_address_read'}<=set(u)
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];assert not set(app)&set(u)
 report=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,remaining_application_imports=[],application_imports_resolved=app,whole_startup_graph_executed=False,physical_reset_or_retention_verified=False,application_linked=False,original_instruction_identity=False,gates=['Reset decoder import resolves to a C kernel with a raw incoming-register forwarding bridge; three retained diagnostic providers are explicit imports.','Logger sources are available in the larger bundle; per-body verification uses named logger/diagnostic fixtures.','Shared DIF string overlaps the prior ctype read-only window by25 bytes; final source data alias/placement remains open.','Raw private ABI, GXT pointer placement/alias gate, complete startup, physical reset/retention and byte-identical image remain open.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Reset decoder source-linked; three retained diagnostics remain;',len(u),'transitive startup imports')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Reuse source CRC/retained context and attributable EABI clear for reset writers."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-reset-writer-runtime';out.mkdir(exist_ok=True);reports={};objects=[];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-reset-writer','native_reset_writer.o'),('native-reset-retained','reset-retained-source.o'),('runtime','memory-runtime.o'),('native-reset-retained-runtime','native-reset-retained-runtime.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;expected=r.get('linked_sha256') or r.get('relocatable_sha256') or r['units'][0]['object_sha256'];assert sha(obj)==expected;reports[str(rp.relative_to(BASE))]=sha(rp);objects.append(obj)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 clear=out/'eabi-clear-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=__aeabi_memclr',str(objects[2]),'-o',str(clear)],check=True)
 small=out/'reset-writer-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(objects[1]),str(clear),'-o',str(small)],check=True);su,sd=undefined_symbols(small);assert not su
 linked=out/'native-reset-writer-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(objects[3]),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert 'r1_reset_trace_capture_site_adapter' not in u
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];assert not set(app)&set(u)
 report=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},clear_object_sha256=sha(clear),writer_object_sha256=sha(small),writer_undefined_symbols=su,writer_defined_symbols=sd,linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,remaining_application_imports=[],application_imports_resolved=app,whole_startup_graph_executed=False,physical_retention_or_reset_verified=False,application_linked=False,original_instruction_identity=False,gates=['Reset writer bundle reuses actual source CRC/getters/context and existing attributable EABI/memory-clear source with zero imports.','Capture adapter resolves startup import; the source architectural PC probe needs its recovered address for native stored-PC equality.','Writer validation/clear pointer ordering and private raw ABI remain separate from physical retention and atomicity.','Prior GXT pointer alias and shared literal gates remain open; final placement/compiler and byte-identical firmware remain unproven.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Reset writer source bundle zero imports;',len(u),'transitive startup imports remain')
if __name__=='__main__':main()

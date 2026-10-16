#!/usr/bin/env python3
"""Link retained getters and existing source CRC16 into available startup source."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-reset-retained-runtime';out.mkdir(exist_ok=True);reports={};objects=[];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-reset-retained','reset-retained-source.o'),('native-reset-decoder-runtime','native-reset-decoder-runtime.o'),('native-reset-decoder','native_reset_decoder.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);reports[str(rp.relative_to(BASE))]=sha(rp);objects.append(obj)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-reset-retained-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects[:2]),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert not {'r1_reset_trace_byte_read','r1_reset_trace_program_counter_read','r1_reset_trace_return_address_read','r1_stock_crc16_modbus'}&set(u)
 selected=out/'reset-diagnostic-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_reset_reason_decode_and_report',str(objects[0]),str(objects[2]),'-o',str(selected)],check=True);du,dd=undefined_symbols(selected);assert du==['nrf_log_frontend_std_0','nrf_log_frontend_std_1','r1_structured_log_format','r1_structured_log_mode_get']
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];assert not set(app)&set(u)
 report=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),diagnostic_object_sha256=sha(selected),diagnostic_undefined_symbols=du,diagnostic_defined_symbols=dd,undefined_symbols=u,defined_symbols=d,remaining_application_imports=[],application_imports_resolved=app,whole_startup_graph_executed=False,physical_retention_verified=False,application_linked=False,original_instruction_identity=False,gates=['Retained byte/PC/LR getters and source CRC16 now resolve the decoder diagnostic imports.','Context cold24-byte source view does not initialize or consume the retained record itself.','Writer/capture, physical retention and whole startup remain unverified; prior raw GXT pointer and shared literal gates remain open.','Raw private frames, final source state/link ownership, original compiler and byte-identical firmware remain open.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Retained getters + CRC source-linked;',len(u),'transitive startup imports remain')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Compile unmodified Nordic vector setup with isolated recovered dual-log macros."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-dfu-vector-set';out.mkdir(exist_ok=True);rp=BASE/'application-sdk/report.json';sdk=json.loads(rp.read_text());seed=next(u for u in sdk['units'] if u['source'].endswith('/nrf_dfu_svci.c'));src=ROOT/seed['source'];assert sha(src)==seed['source_sha256'];base=seed['command'][1:seed['command'].index('-c')];base=['-I'+str(ROOT/'r1/source-config/runtime/dfu-vector-log'),*base];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),str(rp.relative_to(ROOT)):sha(rp)};units=[]
 for source,name in [(src,'nrf_dfu_svci'),(ROOT/'r1/components/runtime/native_dfu_vector_log_port.c','log_port')]:
  obj=out/(name+'.o');dep=out/(name+'.d');cmd=['clang',*base,'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
  for item in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():p=Path(item);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
  u,d=undefined_symbols(obj);units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=u,defined=d))
 selected=out/'native-dfu-vector-set.o';cmd=['arm-none-eabi-ld','-r','--gc-sections','--undefined=nrf_dfu_svci_vector_table_set',str(out/'nrf_dfu_svci.o'),str(out/'log_port.o'),'-o',str(selected)];subprocess.run(cmd,check=True);u,d=undefined_symbols(selected);assert u==['nrf_log_frontend_std_0','nrf_log_frontend_std_1','r1_structured_log_format','r1_structured_log_mode_get']
 report=dict(units=units,inputs=inputs,selection_command=cmd,linked_sha256=sha(selected),undefined_symbols=u,defined_symbols=d,upstream_source_unmodified=True,upstream_source_sha256=sha(src),provider_report_sha256=sha(rp),sdk_archive_sha256=sdk['sdk_archive_sha256'],macro_adaptation='R1 dual logging only; upstream boot fallback, supervisor bridge and return algorithm unchanged',native_scope='nrf_dfu_svci_vector_table_set202 bytes; upstream unset compiled but not selected or admitted here',image_linked=False,instruction_identity=False,gates=['Actual SVC19 handler, physical MBR/UICR reads and vector ownership remain external.','Logging ports and source constant placement are separately recovered R1 adaptations.','Exact original compiler, raw ABI/private frame and whole image byte identity remain open.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Unmodified Nordic vector setup compiled with source dual-log adapter; only four logging imports remain')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Compile source-owned native terminal overflow logging callback."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-stack-overflow';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/tasks.c'));source=ROOT/'r1/components/board/native_stack_overflow.c';obj=out/'stack-overflow.o';dep=out/'stack-overflow.d';cmd=['clang',*row['command'][1:row['command'].index('-c')],'-fshort-enums','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  q=Path(p);inputs[str(q.relative_to(ROOT)) if q.is_relative_to(ROOT) else p]=sha(q)
 u,d=undefined_symbols(obj);assert u==['nrf_log_frontend_dequeue','nrf_log_frontend_std_1','r1_structured_log_format','r1_structured_log_mode_get'],u
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(obj),remaining_symbols=u,source_configuration={'ring_severity':'0x0c400000','nordic_severity':'0x001c0003','nordic_module':28,'terminal_behavior':'drain Nordic logger untilfalse, then permanent loop; no explicit BASEPRI change'},scope='Native overflow callback with independent mode reads, exact two producer formats, drain and terminal loop; logging providers remain actual source dependencies'),indent=2)+'\n');print('Overflow callback compiled; remaining:',u)
if __name__=='__main__':main()

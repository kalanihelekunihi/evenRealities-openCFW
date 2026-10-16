#!/usr/bin/env python3
"""Select unchanged task-count getter, sharing the native kernel count word."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-task-count';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/tasks.c'));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();m=re.search(r'^UBaseType_t uxTaskGetNumberOfTasks\([^;{]*\)\s*\{',text,re.M);assert m;end=text.index('\n}',m.end())+2;part=text[m.start():end];license=raw[:raw.index(b'*/')+2];prefix=b'\n#include "FreeRTOS.h"\n#include "task.h"\nextern volatile UBaseType_t uxCurrentNumberOfTasks;\n';source=out/'task-count.c';source.write_bytes(license+prefix+part.encode());obj=out/'task-count.o';dep=out/'task-count.d';cmd=['clang',*row['command'][1:row['command'].index('-c')],'-fshort-enums','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  q=Path(p);inputs[str(q.relative_to(ROOT)) if q.is_relative_to(ROOT) else p]=sha(q)
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0])],inputs=inputs,upstream_source=row['source'],upstream_sha256=sha(up),source_slices=[dict(name='uxTaskGetNumberOfTasks',start=m.start(),end=end,sha256=hashlib.sha256(part.encode()).hexdigest())],license_bytes=len(license),license_sha256=hashlib.sha256(license).hexdigest(),generated_prefix=prefix.decode(),rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(obj),remaining_symbols=undefined_symbols(obj)[0],scope='Unchanged pinned task-count query, existing shared count at0x20007824; no new kernel state ownership'),indent=2)+'\n');print('Task-count query compiled')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Compile unchanged kernel sleep status and tick stepping."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-sleep-kernel';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/tasks.c'));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();slices=[];parts=[]
 for name in ('eTaskConfirmSleepModeStatus','vTaskStepTick'):
  m=re.search(r'^[ \t]*(?:eSleepModeStatus|void) '+name+r'\s*\([^;{]*\)\s*\{',text,re.M);assert m;clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);depth=1;end=m.end()
  while depth:depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
  if text[end:end+1]=='\n':end+=1
  part=text[m.start():end];parts.append(part);slices.append(dict(name=name,start=m.start(),end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
 license_part=raw[:raw.index(b'*/')+2];source=out/'sleep-kernel.c';source.write_bytes(license_part+b'\n#include "sleep_kernel_contract.h"\n'+b'\n'.join(p.encode() for p in parts));obj=out/'sleep-kernel.o';dep=out/'sleep-kernel.d';flags=row['command'][1:row['command'].index('-c')];cmd=['clang',*flags,'-O0','-fshort-enums','-fno-delete-null-pointer-checks','-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-I',str(ROOT/'r1/source-config/rtos'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
 u,d=undefined_symbols(obj);assert set(u)=={'xPendingReadyList','xSuspendedTaskList','uxCurrentNumberOfTasks','xYieldPending','xPendedTicks','xNextTaskUnblockTime','vPortEnterCritical','vPortExitCritical'},u
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,upstream_source=row['source'],upstream_sha256=sha(up),license_bytes=len(license_part),license_sha256=hashlib.sha256(license_part).hexdigest(),source_slices=slices,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(obj),remaining_symbols=u,scope='Unchanged pinned kernel sleep status/tick step; existing native state ownership preserved'),indent=2)+'\n');print('Kernel sleep dependencies compiled; remaining:',u)
if __name__=='__main__':main()

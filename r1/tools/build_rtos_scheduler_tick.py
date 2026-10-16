#!/usr/bin/env python3
"""Select unchanged pinned tick/event bodies/macros with native state/prefix ABI."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-scheduler-tick';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/tasks.c'));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();slices=[];parts=[]
 for name in ('xTaskIncrementTick','xTaskRemoveFromEventList','prvResetNextTaskUnblockTime'):
  match=re.search(r'^(?:static )?(?:void|BaseType_t) '+name+r'\([^\n]*\)\r?\n\{',text,re.M);assert match;start=match.start();end=text.index('\n}',match.end())+2
  if text[end:end+2]=='\r\n':end+=2
  part=text[start:end];parts.append(part);slices.append(dict(name=name,start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
 for name in ('taskRECORD_READY_PRIORITY','prvAddTaskToReadyList','taskSWITCH_DELAYED_LISTS'):
  match=re.search(r'^ *#define '+name+r'\(',text,re.M);assert match;start=match.start();end=text.index('\n',start)+1
  while text[start:end].rstrip().endswith('\\'):end=text.index('\n',end)+1
  part=text[start:end];parts.insert(0,part);slices.append(dict(name=name,start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
 license_part=raw[:raw.index(b'*/')+2];source=out/'scheduler-tick.c';source.write_bytes(license_part+b'\n#include "scheduler_tick_contract.h"\n'+b'\n'.join(p.encode() for p in parts));obj=out/'scheduler-tick.o';dep=out/'scheduler-tick.d';flags=row['command'][1:row['command'].index('-c')];command=['clang',*flags,'-fshort-enums','-fwrapv','-O0','-fno-inline','-I',str(ROOT/'r1/source-config/rtos'),'-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
 u,d=undefined_symbols(obj);(out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,upstream_source=row['source'],upstream_sha256=sha(up),license_bytes=len(license_part),license_sha256=hashlib.sha256(license_part).hexdigest(),source_slices=slices,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(obj),remaining_symbols=u,scope='Unchanged pinned FreeRTOS tick/event-list/reset-unblock bodies and delayed/ready-list macros, native shared state and accessed TCB prefix only',limitations=['Full TCB size/allocation remains gated. Scheduler state and critical providers are separate dependencies.']),indent=2)+'\n');print('Tick/event bodies compiled; remaining:',u)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Select unchanged pinned tick/event bodies/macros with native state/prefix ABI."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-task-wait';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/tasks.c'));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();slices=[];parts=[]
 for name in ('vTaskInternalSetTimeOutState','vTaskMissedYield','vTaskPlaceOnEventList','xTaskCheckForTimeOut','xTaskPriorityDisinherit','prvAddCurrentTaskToDelayedList'):
  match=re.search(r'^[ \t]*(?:static )?(?:void|BaseType_t) '+name+r'\([^;{]*\)\s*\{',text,re.M);assert match;start=match.start();clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);depth=1;end=match.end()
  while depth:
   depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
  if text[end:end+2]=='\r\n':end+=2
  part=text[start:end];parts.append(part);slices.append(dict(name=name,start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
 for name in ('taskRECORD_READY_PRIORITY','prvAddTaskToReadyList','portRESET_READY_PRIORITY'):
  match=re.search(r'^ *#define '+name+r'\(',text,re.M);assert match;start=match.start();end=text.index('\n',start)+1
  while text[start:end].rstrip().endswith('\\'):end=text.index('\n',end)+1
  part=text[start:end];parts.insert(0,part);slices.append(dict(name=name,start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
 match=re.search(r'^const volatile UBaseType_t uxTopUsedPriority[^\n]*\n',text,re.M);assert match;part=match.group();parts.insert(0,part);slices.append(dict(name='uxTopUsedPriority',start=match.start(),end=match.end(),sha256=hashlib.sha256(part.encode()).hexdigest()))
 license_part=raw[:raw.index(b'*/')+2];source=out/'task-wait.c';source.write_bytes(license_part+b'\n#include "task_wait_contract.h"\n'+b'\n'.join(p.encode() for p in parts));obj=out/'task-wait-raw.o';dep=out/'task-wait.d';flags=row['command'][1:row['command'].index('-c')];command=['clang',*flags,'-fshort-enums','-fwrapv','-O0','-fno-inline','-I',str(ROOT/'r1/source-config/rtos'),'-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
 lr=next(x for x in original['units'] if x['source'].endswith('/list.c'));ls=ROOT/lr['source'];assert sha(ls)==lr['source_sha256'];lo=out/'list.o';lc=['clang',*lr['command'][1:lr['command'].index('-c')],'-fshort-enums','-fno-inline','-MD','-MF',str(out/'list.d'),'-c',str(ls),'-o',str(lo)];subprocess.run(lc,check=True)
 for p in (out/'list.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
  path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
 inputs[lr['source']]=sha(ls);selected=out/'task-wait.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in ('uxTopUsedPriority','vTaskInternalSetTimeOutState','vTaskMissedYield','vTaskPlaceOnEventList','xTaskCheckForTimeOut','xTaskPriorityDisinherit')],str(obj),str(lo),'-o',str(selected)],check=True)
 u,d=undefined_symbols(obj);(out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),defined=d,undefined=u),dict(source=lr['source'],source_sha256=sha(ls),command=lc,compiled=True,object_sha256=sha(lo),undefined=undefined_symbols(lo)[0],defined=undefined_symbols(lo)[1])],inputs=inputs,upstream_source=row['source'],upstream_sha256=sha(up),license_bytes=len(license_part),license_sha256=hashlib.sha256(license_part).hexdigest(),source_slices=slices,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(selected),remaining_symbols=undefined_symbols(selected)[0],list_unit=dict(source=lr['source'],source_sha256=sha(ls),command=lc,object_sha256=sha(lo)),scope='Unchanged pinned FreeRTOS timeout/wait/mutex bodies and list primitives, native shared state and104-byte accessed TCB prefix',limitations=['Full TCB size/allocation remains gated. Scheduler state and critical providers are separate dependencies.']),indent=2)+'\n');print('Task wait/mutex bodies compiled; remaining:',undefined_symbols(selected)[0])
if __name__=='__main__':main()

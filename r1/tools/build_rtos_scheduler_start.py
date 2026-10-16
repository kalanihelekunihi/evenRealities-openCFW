#!/usr/bin/env python3
"""Build pinned scheduler/timer construction and typed source-owned static callbacks."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-scheduler-start';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());units=[];inputs={};objects=[];origins=[]
 for suffix,names,header,target in [('/tasks.c',('vTaskStartScheduler',),'startup_task_contract.h','scheduler'),('/timers.c',('prvCheckForValidListAndQueue','xTimerCreateTimerTask'),'startup_timer_contract.h','timer')]:
  row=next(x for x in original['units'] if x['source'].endswith(suffix));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);slices=[];parts=[]
  if target=='timer':
   start=text.index('    typedef struct tmrTimerParameters');end=text.index('    } DaemonTaskMessage_t;',start)+len('    } DaemonTaskMessage_t;');part=text[start:end];parts.append(part);slices.append(dict(name='timer_message_types',start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
  for name in names:
   m=re.search(r'^[ \t]*(?:static )?(?:void|BaseType_t) '+name+r'\s*\([^;{]*\)\s*\{',text,re.M);assert m,name;depth=1;end=m.end()
   while depth:depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
   part=text[m.start():end];parts.append(part);slices.append(dict(name=name,start=m.start(),end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
  license_part=raw[:raw.index(b'*/')+2];source=out/(target+'.c');extra=b'\nvoid r1_native_timer_infrastructure(void) __attribute__((alias("prvCheckForValidListAndQueue")));\n_Static_assert(sizeof(DaemonTaskMessage_t)==16,"native timer queue message");\n' if target=='timer' else b'\nTaskHandle_t xIdleTaskHandle;\n';source.write_bytes(license_part+('\n#include "'+header+'"\n').encode()+b'\n'.join(p.encode() for p in parts)+extra);obj=out/(target+'.o');dep=out/(target+'.d');cmd=['clang',*row['command'][1:row['command'].index('-c')],'-O0','-fshort-enums','-fno-inline','-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);objects.append(obj)
  for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
  units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0]));origins.append(dict(source=row['source'],sha256=sha(up),target=target,license_bytes=len(license_part),license_sha256=hashlib.sha256(license_part).hexdigest(),slices=slices))
 row=next(x for x in original['units'] if x['source'].endswith('/static_task_memory.c'));source=ROOT/row['source'];assert sha(source)==row['source_sha256'];obj=out/'static-memory.o';dep=out/'static-memory.d';cmd=['clang',*row['command'][1:row['command'].index('-c')],'-fshort-enums','-I',str(ROOT/'r1/source-config/rtos'),'-include',str(ROOT/'r1/source-config/rtos/startup_task_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);objects.append(obj)
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
 units.append(dict(source=row['source'],source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0]));selected=out/'scheduler-start.o';roots=('vTaskStartScheduler','xTimerCreateTimerTask','r1_native_timer_infrastructure','vApplicationGetIdleTaskMemory','vApplicationGetTimerTaskMemory');subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],*map(str,objects),'-o',str(selected)],check=True)
 (out/'report.json').write_text(json.dumps(dict(units=units,inputs=inputs,origins=origins,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(selected),remaining_symbols=undefined_symbols(selected)[0],source_configuration=dict(static_tcb_bytes=112,stack_words=256,timer_priority=53,timer_queue_length=32,timer_message_bytes=16,queue_registry_size=0),scope='Unchanged pinned scheduler/timer-task creation and timer infrastructure plus unchanged typed source-owned static memory callbacks. Port start and timer task body remain explicit providers.'),indent=2)+'\n');print('Scheduler/timer construction compiled; remaining:',undefined_symbols(selected)[0])
if __name__=='__main__':main()

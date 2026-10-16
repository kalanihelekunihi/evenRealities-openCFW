#!/usr/bin/env python3
"""Build R1 task construction plus unchanged pinned ready-list/port bodies."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def body(text,name):
 m=re.search(r'^[ \t]*(?:static )?(?:void|BaseType_t|StackType_t \*)\s*'+name+r'\([^;{]*\)\s*\{',text,re.M);assert m,name;clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);depth=1;end=m.end()
 while depth:depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
 if text[end:end+2]=='\r\n':end+=2
 return m.start(),end

def main():
 out=BASE/'native-task-construction';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());units=[];objects=[];inputs={};origins=[]
 for suffix,names,macros,header,target in [('/tasks.c',('prvAddNewTaskToReadyList','prvInitialiseTaskLists'),('taskRECORD_READY_PRIORITY','prvAddTaskToReadyList'),'task_construction_contract.h','ready'),('/port_cmsis.c',('pxPortInitialiseStack','prvTaskExitError'),(),'task_stack_contract.h','stack')]:
  row=next(x for x in original['units'] if x['source'].endswith(suffix));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();parts=[];slices=[]
  for n in names:
   start,end=body(text,n);part=text[start:end];parts.append(part);slices.append(dict(name=n,start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
  for n in macros:
   m=re.search(r'^ *#define '+n+r'\(',text,re.M);assert m;start=m.start();end=text.index('\n',start)+1
   while text[start:end].rstrip().endswith('\\'):end=text.index('\n',end)+1
   part=text[start:end];parts.insert(0,part);slices.append(dict(name=n,start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
  license_part=raw[:raw.index(b'*/')+2];extra=b'\nvoid r1_native_task_add_ready(r1_native_tcb *) __attribute__((alias("prvAddNewTaskToReadyList")));\n' if target=='ready' else b'';source=out/(target+'.c');source.write_bytes(license_part+('\n#include "'+header+'"\n').encode()+b'\n'.join(p.encode() for p in parts)+extra);origins.append(dict(source=row['source'],sha256=sha(up),target=target,license_bytes=len(license_part),license_sha256=hashlib.sha256(license_part).hexdigest(),slices=slices))
  flags=row['command'][1:row['command'].index('-c')];obj=out/(target+'.o');dep=out/(target+'.d');cmd=['clang',*flags,'-O0','-fshort-enums','-fno-inline','-I',str(ROOT/'r1/components/board'),'-I',str(ROOT/'r1/source-config/rtos'),'-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
  for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
  u,d=undefined_symbols(obj);units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u));objects.append(obj)
 row=next(x for x in original['units'] if x['source'].endswith('/tasks.c'));flags=row['command'][1:row['command'].index('-c')];source=ROOT/'r1/components/board/native_task_construction.c';obj=out/'construction.o';dep=out/'construction.d';cmd=['clang',*flags,'-O0','-fshort-enums','-fno-inline','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
 u,d=undefined_symbols(obj);units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u));objects.append(obj)
 lr=json.loads((BASE/'rtos-task-wait/report.json').read_text())['list_unit'];lo=BASE/'rtos-task-wait/list.o';assert sha(lo)==lr['object_sha256'];li=out/'list-item.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=vListInitialiseItem',str(lo),'-o',str(li)],check=True);objects.append(li)
 inputs[lr['source']]=sha(ROOT/lr['source']);units.append(dict(source=lr['source'],source_sha256=sha(ROOT/lr['source']),command=['arm-none-eabi-ld','-r','--gc-sections','--undefined=vListInitialiseItem',str(lo),'-o',str(li)],compiled=True,object_sha256=sha(li),defined=undefined_symbols(li)[1],undefined=undefined_symbols(li)[0]));selected=out/'task-construction.o';roots=('r1_native_task_initialize','r1_native_task_create','r1_native_task_create_static','r1_native_task_add_ready','pxPortInitialiseStack','r1_native_initial_xpsr','uxTaskNumber','xTasksWaitingTermination');subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],*map(str,objects),'-o',str(selected)],check=True);u,d=undefined_symbols(selected)
 (out/'report.json').write_text(json.dumps(dict(units=units,inputs=inputs,origins=origins,rtos_report_sha256=sha(BASE/'rtos/report.json'),sdk_port_report_sha256=sha(BASE/'rtos-critical/report.json'),provider_aliases={'xTaskCreate':'r1_native_task_create','xTaskCreateStatic':'r1_native_task_create_static'},list_report_sha256=sha(BASE/'rtos-task-wait/report.json'),list_input_object_sha256=sha(lo),list_selected_object_sha256=sha(li),selected_object_sha256=sha(selected),remaining_symbols=u,scope='Native112-byte task constructors/initializer, unchanged kernel ready/list-init and Nordic initial-stack/return-error bodies; scheduler start/context switching remain separate gates'),indent=2)+'\n');print('Task construction compiled; remaining:',u)
if __name__=='__main__':main()

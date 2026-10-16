#!/usr/bin/env python3
"""Compile unchanged pinned FreeRTOS idle task with authenticated scoped hook."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-idle';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/tasks.c'));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();m=re.search(r'^static portTASK_FUNCTION\( prvIdleTask, pvParameters \)\s*\{',text,re.M);assert m;clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);depth=1;end=m.end()
 while depth:depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
 if text[end:end+2]=='\r\n':end+=2
 part=text[m.start():end].encode();license_part=raw[:raw.index(b'*/')+2];source=out/'idle.c';source.write_bytes(license_part+b'\n#include "idle_contract.h"\n'+part+b'\nvoid r1_native_idle_watchdog_hook(void) { (void)r1_native_watchdog_hw_feed_thunk(); }\nvoid r1_native_idle_task(void *) __attribute__((alias("prvIdleTask")));\n');obj=out/'idle.o';dep=out/'idle.d';flags=row['command'][1:row['command'].index('-c')];cmd=['clang',*flags,'-O0','-fshort-enums','-fno-inline','-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
 u,d=undefined_symbols(obj);assert set(u)=={'pxReadyTasksLists','r1_native_task_idle_cleanup','r1_native_expected_idle_time','r1_native_watchdog_hw_feed_thunk','vTaskSuspendAll','xTaskResumeAll','xNextTaskUnblockTime','vPortSuppressTicksAndSleep'},u
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,upstream_source=row['source'],upstream_sha256=sha(up),license_bytes=len(license_part),license_sha256=hashlib.sha256(license_part).hexdigest(),source_slices=[dict(name='prvIdleTask',start=m.start(),end=end,sha256=hashlib.sha256(part).hexdigest())],rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(obj),remaining_symbols=u,provider_binding={'vApplicationIdleHook':'r1_native_idle_watchdog_hook','r1_native_idle_watchdog_hook':'r1_native_watchdog_hw_feed_thunk'},source_configuration={'configUSE_IDLE_HOOK':1,'configUSE_PREEMPTION':1,'configIDLE_SHOULD_YIELD':1,'configUSE_TICKLESS_IDLE':1,'configEXPECTED_IDLE_TIME_BEFORE_SLEEP':2},scope='Complete unchanged kernel idle task with scoped native hook selection; port tick suppression remains an explicit provider'),indent=2)+'\n');print('Idle task compiled; remaining:',u)
if __name__=='__main__':main()

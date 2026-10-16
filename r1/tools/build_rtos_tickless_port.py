#!/usr/bin/env python3
"""Compile pinned Nordic RTC tick suppression with source-owned native bindings."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-tickless-port';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/port_cmsis_systick.c'));source=ROOT/row['source'];assert sha(source)==row['source_sha256'];obj=out/'port-raw.o';dep=out/'port.d';flags=row['command'][1:row['command'].index('-c')];cmd=['clang',*flags,'-fshort-enums','-include',str(ROOT/'r1/source-config/rtos/tickless_port_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
 selected=out/'tickless-port.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=vPortSuppressTicksAndSleep',str(obj),'-o',str(selected)],check=True);u,d=undefined_symbols(selected)
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=row['source'],source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0])],inputs=inputs,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(selected),remaining_symbols=u,source_configuration={'configTICK_SOURCE':'RTC1','configUSE_TICKLESS_IDLE':1,'configUSE_TICKLESS_IDLE_SIMPLE_DEBUG':1,'configEXPECTED_IDLE_TIME_BEFORE_SLEEP':2},scope='Unchanged pinned Nordic RTC sleep port with scoped native error and FPU pre-sleep bindings; other source sections discarded'),indent=2)+'\n');print('Nordic RTC sleep port compiled; remaining:',u)
if __name__=='__main__':main()

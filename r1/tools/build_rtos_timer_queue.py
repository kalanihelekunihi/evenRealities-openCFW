#!/usr/bin/env python3
"""Compile unchanged pinned FreeRTOS timer queue receive/restricted-wait providers."""
import hashlib,json,subprocess
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-timer-queue';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());rows=[];objects=[];inputs={}
 for suffix in ('/queue.c',):
  row=next(x for x in original['units'] if x['source'].endswith(suffix));source=ROOT/row['source'];assert sha(source)==row['source_sha256'];cmd=row['command'];flags=cmd[1:cmd.index('-c')];obj=out/(source.stem+'.o');dep=out/(source.stem+'.d')
  command=['clang',*flags,'-fshort-enums','-fno-delete-null-pointer-checks','-fno-inline','-include',str(ROOT/'r1/source-config/rtos/queue_operations_contract.h'),'-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
  for path in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():inputs[str(Path(path).relative_to(ROOT)) if Path(path).is_relative_to(ROOT) else path]=sha(Path(path))
  undefined,defined=undefined_symbols(obj);rows.append(dict(source=row['source'],source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
 selected=out/'timer-queue.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in ('xQueueReceive','vQueueWaitForMessageRestricted')],*map(str,objects),'-o',str(selected)],check=True);remaining,_=undefined_symbols(selected)
 (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(selected),remaining_symbols=remaining,scope='Pinned FreeRTOS timer queue receive/restricted-wait/copy/unlock providers; task-wait and memory/critical backends remain explicit',limitations=['Selected variant accesses the established native queue/TCB contracts; combined timer graph and whole-image layout remain separate gates.','Native assertions apply only to selected variant; original instruction identity remains unproven.']),indent=2)+'\n');print('Pinned FreeRTOS timer queue compiled')
if __name__=='__main__':main()

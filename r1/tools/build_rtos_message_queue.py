#!/usr/bin/env python3
"""Compile unchanged CMSIS queue wrappers with the authenticated native queue ABI."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-message-queue';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/cmsis_os2.c'));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();slices=[];parts=[]
 for name in ('IRQ_Context','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet','osMessageQueueGetCapacity','osMessageQueueGetCount'):
  m=re.search(r'^(?:__STATIC_INLINE uint32_t|osMessageQueueId_t|osStatus_t|uint32_t) '+name+r'\s*\([^;{]*\)\s*\{',text,re.M);assert m;clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);depth=1;end=m.end()
  while depth:depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
  if text[end:end+1]=='\n':end+=1
  part=text[m.start():end];parts.append(part);slices.append(dict(name=name,start=m.start(),end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
 for name,pattern in [('IS_IRQ_MASKED','__get_BASEPRI'),('IS_IRQ_MODE','__get_IPSR')]:
  m=next(m for m in re.finditer(r'^#define '+name+r'\([^\n]*\n',text,re.M) if pattern in m.group());part=m.group();parts.insert(0,part);slices.append(dict(name=name,start=m.start(),end=m.end(),sha256=hashlib.sha256(part.encode()).hexdigest()))
 license_part=raw[:raw.index(b'*/')+2];source=out/'message-queue.c';source.write_bytes(license_part+b'\n#include "message_queue_contract.h"\n'+b'\n'.join(p.encode() for p in parts));obj=out/'message-queue.o';dep=out/'message-queue.d';flags=row['command'][1:row['command'].index('-c')];cmd=['clang',*flags,'-fshort-enums','-fno-delete-null-pointer-checks','-I',str(ROOT/'r1/source-config/rtos'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
 u,d=undefined_symbols(obj);assert set(u)=={'xQueueGenericCreate','xQueueGenericCreateStatic','xQueueGenericSend','xQueueGenericSendFromISR','xQueueReceive','xQueueReceiveFromISR','uxQueueMessagesWaiting','uxQueueMessagesWaitingFromISR','xTaskGetSchedulerState'},u
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,upstream_source=row['source'],upstream_sha256=sha(up),license_bytes=len(license_part),license_sha256=hashlib.sha256(license_part).hexdigest(),source_slices=slices,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(obj),remaining_symbols=u,scope='Unchanged pinned CMSIS message queue creation/send/receive/capacity/count and IRQ predicate; native80-byte static queue/24-byte attributes; registry0 scoped to authenticated native constructor; kernel defaults preserved'),indent=2)+'\n');print('CMSIS message queue compiled; remaining:',u)
if __name__=='__main__':main()

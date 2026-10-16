#!/usr/bin/env python3
"""Compile pinned C ARM context port and unchanged kernel task selection."""
import hashlib,json,re,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-context-port';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/tasks.c'));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);parts=[];slices=[]
 m=re.search(r'^void vTaskSwitchContext\([^;{]*\)\s*\{',text,re.M);assert m;end=m.end();depth=1
 while depth:depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
 part=text[m.start():end];parts.append(part);slices.append(dict(name='vTaskSwitchContext',start=m.start(),end=end,sha256=hashlib.sha256(part.encode()).hexdigest()));m=re.search(r'^ *#define taskSELECT_HIGHEST_PRIORITY_TASK\(',text,re.M);assert m;start=m.start();end=text.index('\n',start)+1
 while text[start:end].rstrip().endswith('\\'):end=text.index('\n',end)+1
 part=text[start:end];parts.insert(0,part);slices.append(dict(name='taskSELECT_HIGHEST_PRIORITY_TASK',start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()));license_part=raw[:raw.index(b'*/')+2];source=out/'selection.c';source.write_bytes(license_part+b'\n#include "context_contract.h"\n'+b'\n'.join(p.encode() for p in parts));flags=row['command'][1:row['command'].index('-c')];units=[];objects=[];inputs={}
 sdk=ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/external/freertos/portable/GCC/nrf52/port.c';archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as z:assert z.read('nRF5_SDK_17.1.0_ddde560/external/freertos/portable/GCC/nrf52/port.c')==sdk.read_bytes()
 for name,path in [('selection',source),('context',sdk),('vectors',ROOT/'r1/components/rtos/native_context_vectors.c')]:
  obj=out/(name+'.o');dep=out/(name+'.d');cmd=['clang',*flags,'-fshort-enums','-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(path),'-o',str(obj)];subprocess.run(cmd,check=True);objects.append(obj)
  for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   q=Path(p);inputs[str(q.relative_to(ROOT)) if q.is_relative_to(ROOT) else p]=sha(q)
  units.append(dict(source=str(path.relative_to(ROOT)),source_sha256=sha(path),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0]))
 selected=out/'context-port.o';roots=('vPortStartFirstTask','SVC_Handler','PendSV_Handler','vTaskSwitchContext','__isr_vector','r1_application_svc_vector','r1_application_pendsv_vector');subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],*map(str,objects),'-o',str(selected)],check=True)
 (out/'report.json').write_text(json.dumps(dict(units=units,inputs=inputs,upstream_source=row['source'],upstream_sha256=sha(up),source_slices=slices,license_bytes=len(license_part),license_sha256=hashlib.sha256(license_part).hexdigest(),sdk_source=str(sdk.relative_to(ROOT)),sdk_source_sha256=sha(sdk),sdk_zip_sha256=sha(archive),rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(selected),remaining_symbols=undefined_symbols(selected)[0],source_owned_vector_records=[{'address':'0x27000','symbol':'__isr_vector','native_value':'0x2003beb8'},{'address':'0x2702c','symbol':'r1_application_svc_vector','native_value':'0x27219'},{'address':'0x27038','symbol':'r1_application_pendsv_vector','native_value':'0x2725d'}],full_vector_table_proven=False,scope='Unchanged pinned C ARM port with explicit inline assembly, unchanged kernel task selection and three source-owned vector words; overflow hook remains explicit provider'),indent=2)+'\n');print('Context C port compiled; remaining:',undefined_symbols(selected)[0])
if __name__=='__main__':main()

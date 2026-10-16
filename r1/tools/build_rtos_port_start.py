#!/usr/bin/env python3
"""Compile unchanged pinned Nordic port start and RTC1 timer setup."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-port-start';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());objects=[];units=[];inputs={};origins=[]
 for suffix,names,macros,target in [('/port_cmsis.c',('vPortEnableVFP','prvTaskExitError','xPortStartScheduler'),('portCORTEX_M4_r0p1_ID','portMAX_8_BIT_VALUE','portTOP_BIT_OF_BYTE'),'port'),('/port_cmsis_systick.c',('vPortSetupTimerInterrupt',),(),'rtc')]:
  row=next(x for x in original['units'] if x['source'].endswith(suffix));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);slices=[];parts=[]
  for name in names:
   matches=list(re.finditer(r'^[ \t]*(?:static )?(?:void|BaseType_t) '+name+r'\s*\([^;{]*\)\s*\{',text,re.M));assert matches,name;m=matches[-1];depth=1;end=m.end()
   while depth:depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
   part=text[m.start():end];parts.append(part);slices.append(dict(name=name,start=m.start(),end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
  for name in macros:
   m=re.search(r'^#define '+name+r'[^\n]*\n',text,re.M);assert m;part=m.group();parts.insert(0,part);slices.append(dict(name=name,start=m.start(),end=m.end(),sha256=hashlib.sha256(part.encode()).hexdigest()))
  license_part=raw[:raw.index(b'*/')+2];source=out/(target+'.c');source.write_bytes(license_part+b'\n#include "port_start_contract.h"\n'+b'\n'.join(p.encode() for p in parts));obj=out/(target+'.o');dep=out/(target+'.d');cmd=['clang',*row['command'][1:row['command'].index('-c')],'-fshort-enums','-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);objects.append(obj)
  for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   path=Path(p);inputs[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else p]=sha(path)
  units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0]));origins.append(dict(source=row['source'],sha256=sha(up),target=target,license_bytes=len(license_part),license_sha256=hashlib.sha256(license_part).hexdigest(),slices=slices))
 selected=out/'port-start.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=xPortStartScheduler','--undefined=vPortSetupTimerInterrupt',*map(str,objects),'-o',str(selected)],check=True);u=undefined_symbols(selected)[0];assert u==['nrf_drv_clock_lfclk_request','vPortStartFirstTask'],u
 (out/'report.json').write_text(json.dumps(dict(units=units,inputs=inputs,origins=origins,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(selected),remaining_symbols=u,source_configuration={'raw_max_syscall_priority':2,'kernel_priority':15,'rtc_prescaler':31,'rtc_irq':17,'cpuid':'0x410fc241'},scope='Unchanged pinned Nordic port start/RTC1 setup/VFP/error bodies; existing private port state words reused by typed address; first task remains explicit provider'),indent=2)+'\n');print('Port startup compiled; remaining:',u)
if __name__=='__main__':main()

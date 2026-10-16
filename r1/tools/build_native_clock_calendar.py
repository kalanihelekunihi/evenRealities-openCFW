#!/usr/bin/env python3
"""Build recovered native calendar ABI using existing source-owned time state."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-clock-calendar';out.mkdir(exist_ok=True);sp=BASE/'structured-time/report.json';seed=json.loads(sp.read_text());flags=seed['units'][0]['command'][1:seed['units'][0]['command'].index('-MD')];flags+=['-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include')];objects=[];units=[];inputs={}
 original=ROOT/'r1/reconstructed/time_calendar/time_calendar.c';text=original.read_text();parts=[text[:text.index('void time_calendar_initialize(')]];slices=[]
 for name in ('time_calendar_broken_down_to_unix','time_calendar_utc_to_calendar','time_calendar_to_utc'):
  import re
  match=re.search(r'(?:int32_t|uint32_t) '+name+r'\(',text);assert match,name
  start=match.start();opening=text.index('{',start);depth=1;end=opening+1
  while depth:
   depth+=(text[end]=='{')-(text[end]=='}');end+=1
  part=text[start:end];parts.append(part);slices.append(dict(name=name,start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
 selected=out/'selected-calendar.c';selected.write_text('\n'.join(parts)+'\n');inputs[str(original.relative_to(ROOT))]=sha(original)
 for source,roots in [(selected,['time_calendar_broken_down_to_unix','time_calendar_utc_to_calendar','time_calendar_to_utc']),(ROOT/'r1/components/board/native_clock_calendar.c',['r1_clock_backend_slot20','r1_clock_backend_slot24'])]:
  raw=out/(source.stem+'.o');obj=out/(source.stem+'-selected.o');dep=out/(source.stem+'.d');cmd=['clang',*flags,'-O0','-fno-inline','-Wno-unused-function','-Wno-unused-const-variable','-Wno-unused-variable','-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True);link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(raw),'-o',str(obj)];subprocess.run(link,check=True)
  for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
  u,d=undefined_symbols(obj);units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u));objects.append(obj)
 obj=out/'clock-calendar.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(obj)],check=True);u,d=undefined_symbols(obj);(out/'report.json').write_text(json.dumps(dict(selected_function_slices=slices,selected_source_sha256=sha(selected),units=units,inputs=inputs,structured_time_report_sha256=sha(sp),selected_object_sha256=sha(obj),remaining_symbols=u,scope='Native calendar ports plus unchanged selected reconstructed converters; forward Gregorian converter, RTC requests and shared time state remain source providers',instruction_identity_proven=False),indent=2)+'\n');print('Native clock calendar compiled; remaining:',u)
if __name__=='__main__':main()

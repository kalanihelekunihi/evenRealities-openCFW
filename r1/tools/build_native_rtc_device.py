#!/usr/bin/env python3
"""Build recovered native calendar ABI using existing source-owned time state."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-rtc-device';out.mkdir(exist_ok=True);sp=BASE/'structured-time/report.json';seed=json.loads(sp.read_text());flags=seed['units'][0]['command'][1:seed['units'][0]['command'].index('-MD')];flags+=['-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include')];objects=[];units=[];inputs={}
 for source,roots in [(ROOT/'r1/components/board/native_rtc_device.c',['r1_native_rtc_snapshot','r1_native_rtc_calendar_write','r1_native_rtc_callback_bind']),(ROOT/'r1/components/runtime/native_memory_move.c',['r1_native_memory_move'])]:
  raw=out/(source.stem+'.o');obj=out/(source.stem+'-selected.o');dep=out/(source.stem+'.d');cmd=['clang',*flags,'-O0','-fno-inline','-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True);link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(raw),'-o',str(obj)];subprocess.run(link,check=True)
  for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
  u,d=undefined_symbols(obj);units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u));objects.append(obj)
 obj=out/'rtc-device.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(obj)],check=True);u,d=undefined_symbols(obj);(out/'report.json').write_text(json.dumps(dict(units=units,inputs=inputs,structured_time_report_sha256=sha(sp),selected_object_sha256=sha(obj),remaining_symbols=u,scope='Native snapshot/calendar-write/callback-bind plus counter and single cold record; open/epoch-init/tick/discovery remain gated',instruction_identity_proven=False),indent=2)+'\n');print('Native RTC device compiled; remaining:',u)
if __name__=='__main__':main()

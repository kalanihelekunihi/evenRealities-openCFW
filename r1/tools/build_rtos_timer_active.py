#!/usr/bin/env python3
"""Compile unchanged pinned timer-active predicate with native44-byte layout."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'rtos-timer-active';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);baseline=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in baseline['units'] if x['source'].endswith('/timers.c'));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);parts=[];slices=[]
 def add(name,start,end):
  part=text[start:end];parts.append(part);slices.append(dict(name=name,start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
 start=text.index('    typedef struct tmrTimerControl');end=text.index('    } DaemonTaskMessage_t;',start)+len('    } DaemonTaskMessage_t;');add('timer_runtime_types',start,end)
 for name in ('tmrNO_DELAY','tmrSTATUS_IS_ACTIVE','tmrSTATUS_IS_STATICALLY_ALLOCATED','tmrSTATUS_IS_AUTORELOAD'):
  m=re.search(r'^ *#define '+name+r'[^\n]*\n',text,re.M);assert m;add(name,m.start(),m.end())
 for name in ('xTimerIsTimerActive',):
  m=re.search(r'^[ \t]*(?:static )?(?:void|TimerHandle_t|BaseType_t) '+name+r'\s*\([^;{]*\)\s*\{',text,re.M);assert m,name;depth=1;end=m.end()
  while depth:depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
  add(name,m.start(),end)
 license=raw[:raw.index(b'*/')+2];extra='\n_Static_assert(sizeof(Timer_t)==44 && offsetof(Timer_t,ucStatus)==40,"native timer status layout");\n';source=out/'timer-active.c';source.write_bytes(license+b'\n#include "timer_active_contract.h"\n'+b'\n'.join(p.encode() for p in parts)+extra.encode());obj=out/'timer-active.o';dep=out/'timer-active.d';cmd=['clang',*row['command'][1:row['command'].index('-c')],'-O0','-fshort-enums','-fno-inline','-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  q=Path(p);inputs[str(q.relative_to(ROOT)) if q.is_relative_to(ROOT) else p]=sha(q)
 result=dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0])],inputs=inputs,upstream_source=row['source'],upstream_sha256=sha(up),source_slices=slices,license_bytes=len(license),license_sha256=hashlib.sha256(license).hexdigest(),generated_suffix=extra,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(obj),remaining_symbols=undefined_symbols(obj)[0],scope='Unchanged pinned timer-active predicate; native44-byte timer, status offset40',limitations=['ISR queue-send provider and combined graph admission remain separate gates. Source compilation does not establish native instruction identity.']);(out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print('Timer active predicate compiled; remaining:',result['remaining_symbols'])
if __name__=='__main__':main()

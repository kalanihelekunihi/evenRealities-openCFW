#!/usr/bin/env python3
"""Select unchanged pinned FIFO and flag-fetch atomic providers without duplicates."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIFO=['nrf_atfifo_clear','nrf_atfifo_init','nrf_atfifo_item_alloc','nrf_atfifo_item_free','nrf_atfifo_item_get','nrf_atfifo_item_put'];INTERNAL=['nrf_atfifo_wspace_req','nrf_atfifo_wspace_close','nrf_atfifo_rspace_req','nrf_atfifo_rspace_close','nrf_atfifo_space_clear'];ATOMIC=['nrf_atomic_flag_set_fetch','nrf_atomic_u32_fetch_or']
def main():
 out=BASE/'sdk-atfifo';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());rows=[];inputs={};objects=[]
 for stem,roots in [('nrf_atfifo',FIFO+INTERNAL),('nrf_atomic',ATOMIC)]:
  row=next(x for x in sdk['units'] if x['source'].endswith('/'+stem+'.c'));source=ROOT/row['source'];flags=row['command'][1:row['command'].index('-c')];raw=out/(stem+'.o');obj=out/(stem+'-selected.o');dep=out/(stem+'.d');cmd=['clang',*flags,'-fno-inline','-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True)
  transforms=[]
  if stem=='nrf_atfifo':
   transform=['arm-none-eabi-objcopy',*['--globalize-symbol='+n for n in INTERNAL],str(raw)];subprocess.run(transform,check=True);transforms.append(transform)
  link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(raw),'-o',str(obj)];subprocess.run(link,check=True)
  strip=['arm-none-eabi-objcopy','--strip-unneeded',str(obj)];subprocess.run(strip,check=True);transforms.append(strip)
  for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
  u,d=undefined_symbols(obj);assert not u,u;rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,object_transforms=transforms,compiled=True,object_sha256=sha(obj),defined=d,undefined=u));objects.append(obj)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 selected=out/'atfifo-atomic.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(selected)],check=True);u,d=undefined_symbols(selected);assert not u
 (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,sdk_report_sha256=sha(sp),selected_object_sha256=sha(selected),defined=d,remaining_symbols=u,scope='Pinned FIFO APIs and exclusive-access helpers plus flag_set_fetch/fetch_or; existing connection-event AND/OR objects are not duplicated',instruction_identity_proven=False),indent=2)+'\n');print('Pinned FIFO/atomic providers compiled with no unresolved symbols')
if __name__=='__main__':main()

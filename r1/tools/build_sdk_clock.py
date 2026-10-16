#!/usr/bin/env python3
"""Compile unchanged pinned clock observers and request helpers with native R1 logging."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ALIASES={'soc_evt_handler':'r1_soc_observer_907fc','sd_state_evt_handler':'r1_sdh_state_observer_890f0','clock_clk_started_notify':'r1_sdk_clock_notify','clock_irq_handler':'r1_sdk_clock_irq_handler','item_enqueue':'r1_sdk_clock_item_enqueue'}
ROOTS=[*ALIASES.values(),'nrf_drv_clock_init','nrf_drv_clock_lfclk_request','nrf_drv_clock_lfclk_release']
def main():
 out=BASE/'sdk-clock';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());rows=[];inputs={};objects=[]
 for stem,roots in [('nrf_drv_clock',ROOTS)]:
  row=next(x for x in sdk['units'] if x['source'].endswith('/'+stem+'.c'));source=ROOT/row['source'];flags=row['command'][1:row['command'].index('-c')];raw=out/(stem+'.o');obj=out/(stem+'-selected.o');dep=out/(stem+'.d');cmd=['clang',*flags,'-fno-inline','-Dm_clock_cb=r1_sdk_clock_control','-include',str(ROOT/'r1/source-config/sdk/clock_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True)
  transforms=[]
  transform=['arm-none-eabi-objcopy',*[arg for old,new in ALIASES.items() for arg in ('--redefine-sym',old+'='+new,'--globalize-symbol='+new)],'--globalize-symbol=r1_sdk_clock_control',str(raw)];subprocess.run(transform,check=True);transforms.append(transform)
  link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(raw),'-o',str(obj)];subprocess.run(link,check=True)
  strip=['arm-none-eabi-objcopy','--strip-unneeded',str(obj)];subprocess.run(strip,check=True);transforms.append(strip)
  for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
  u,d=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,object_transforms=transforms,compiled=True,object_sha256=sha(obj),defined=d,undefined=u));objects.append(obj)
 config_source=ROOT/'r1/components/board/native_clock_logging.c';config_obj=out/'configuration.o';config_dep=out/'configuration.d';config_cmd=['clang',*flags,'-MD','-MF',str(config_dep),'-c',str(config_source),'-o',str(config_obj)];subprocess.run(config_cmd,check=True);objects.append(config_obj)
 for n in config_dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 selected=out/'clock.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(selected)],check=True);u,d=undefined_symbols(selected)
 (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,sdk_report_sha256=sha(sp),selected_object_sha256=sha(selected),defined=d,remaining_symbols=u,configuration_source=str(config_source.relative_to(ROOT)),configuration_command=config_cmd,configuration_object_sha256=sha(config_obj),scope='Pinned clock observers, init, LF requests/releases and notification/enqueue helpers with local structured-log macro contract; nrfx hardware and SDH runtime remain dependencies',instruction_identity_proven=False),indent=2)+'\n');print('Pinned clock source compiled; remaining:', ', '.join(u))
if __name__=='__main__':main()

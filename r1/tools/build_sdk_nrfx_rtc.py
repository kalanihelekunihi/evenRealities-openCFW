#!/usr/bin/env python3
"""Compile pinned nrfx RTC hardware providers without copying vendor bodies."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ROOTS=['nrfx_rtc_init','nrfx_rtc_enable','nrfx_rtc_tick_enable','RTC2_IRQHandler']
def main():
 out=BASE/'sdk-nrfx-rtc';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());row=next(x for x in sdk['units'] if x['source'].endswith('/nrfx_rtc.c'));source=ROOT/row['source'];flags=row['command'][1:row['command'].index('-c')];raw=out/'nrfx_rtc.o';obj=out/'nrfx-rtc-selected.o';dep=out/'nrfx_rtc.d';cmd=['clang',*flags,'-O0','-fno-inline','-Dirq_handler=r1_sdk_rtc_irq_dispatch','-Dm_cb=r1_sdk_rtc_control','-Dm_handlers=r1_sdk_rtc_handlers','-include',str(ROOT/'r1/source-config/sdk/rtc_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True)
 transform=['arm-none-eabi-objcopy','--globalize-symbol=r1_sdk_rtc_irq_dispatch','--globalize-symbol=r1_sdk_rtc_control','--globalize-symbol=r1_sdk_rtc_handlers',str(raw)];subprocess.run(transform,check=True)
 link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in ROOTS],str(raw),'-o',str(obj)];subprocess.run(link,check=True);subprocess.run(['arm-none-eabi-objcopy','--strip-unneeded',str(obj)],check=True);inputs={}
 for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 config_source=ROOT/'r1/components/board/native_rtc_logging.c';config_obj=out/'configuration.o';config_dep=out/'configuration.d';config_cmd=['clang',*flags,'-MD','-MF',str(config_dep),'-c',str(config_source),'-o',str(config_obj)];subprocess.run(config_cmd,check=True)
 for n in config_dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 bridge_source=ROOT/'r1/components/board/native_rtc_driver.c';bridge_obj=out/'driver-bridge.o';bridge_dep=out/'driver-bridge.d';bridge_cmd=['clang',*flags,'-MD','-MF',str(bridge_dep),'-c',str(bridge_source),'-o',str(bridge_obj)];subprocess.run(bridge_cmd,check=True)
 for n in bridge_dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 vector_source=ROOT/'r1/components/board/native_rtc_vector.c';vector_obj=out/'rtc-vector.o';vector_dep=out/'rtc-vector.d';vector_cmd=['clang',*flags,'-MD','-MF',str(vector_dep),'-c',str(vector_source),'-o',str(vector_obj)];subprocess.run(vector_cmd,check=True)
 for n in vector_dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 selected=out/'nrfx-rtc.o';subprocess.run(['arm-none-eabi-ld','-r',str(obj),str(config_obj),str(bridge_obj),str(vector_obj),'-o',str(selected)],check=True);u,d=undefined_symbols(selected);assert set(u)<={'r1_structured_log_mode_get','r1_structured_log_format','nrf_strerror_get'},u
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,object_transforms=[transform,['arm-none-eabi-objcopy','--strip-unneeded',str(obj)]],compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,sdk_report_sha256=sha(sp),selected_object_sha256=sha(selected),vector_source=str(vector_source.relative_to(ROOT)),vector_command=vector_cmd,vector_object_sha256=sha(vector_obj),bridge_source=str(bridge_source.relative_to(ROOT)),bridge_command=bridge_cmd,bridge_object_sha256=sha(bridge_obj),configuration_source=str(config_source.relative_to(ROOT)),configuration_command=config_cmd,configuration_object_sha256=sha(config_obj),remaining_symbols=u,configuration={'NRF_ASSERT_PRESENT':0,'logging':'native structured RTC info adapter; native invalid-state branch has no warning'},scope='Pinned RTC init/enable/tick-enable with actual HAL/NVIC, one instance control/handler arrays and native structured info logging; assertions disabled and native invalid-state branch has no warning',instruction_identity_proven=False),indent=2)+'\n');print('Pinned nrfx RTC hardware compiled')
if __name__=='__main__':main()

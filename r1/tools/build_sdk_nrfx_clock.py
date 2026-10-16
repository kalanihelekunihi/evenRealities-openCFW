#!/usr/bin/env python3
"""Compile pinned nrfx clock hardware providers without copying vendor bodies."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ROOTS=['nrfx_clock_init','nrfx_clock_enable','nrfx_clock_lfclk_start','nrfx_clock_lfclk_stop','POWER_CLOCK_IRQHandler']
def main():
 out=BASE/'sdk-nrfx-clock';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());row=next(x for x in sdk['units'] if x['source'].endswith('/nrfx_clock.c'));source=ROOT/row['source'];flags=row['command'][1:row['command'].index('-c')];raw=out/'nrfx_clock.o';obj=out/'nrfx-clock-selected.o';dep=out/'nrfx_clock.d';cmd=['clang',*flags,'-O0','-fno-inline','-Dm_clock_cb=r1_sdk_nrfx_clock_control','-include',str(ROOT/'r1/source-config/sdk/nrfx_clock_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True)
 transform=['arm-none-eabi-objcopy','--globalize-symbol=r1_sdk_nrfx_clock_control',str(raw)];subprocess.run(transform,check=True)
 link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in ROOTS],str(raw),'-o',str(obj)];subprocess.run(link,check=True);subprocess.run(['arm-none-eabi-objcopy','--strip-unneeded',str(obj)],check=True);inputs={}
 for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 config_source=ROOT/'r1/components/board/native_power_clock_vector.c';config_obj=out/'configuration.o';config_dep=out/'configuration.d';config_cmd=['clang',*flags,'-MD','-MF',str(config_dep),'-c',str(config_source),'-o',str(config_obj)];subprocess.run(config_cmd,check=True)
 for n in config_dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 selected=out/'nrfx-clock.o';subprocess.run(['arm-none-eabi-ld','-r',str(obj),str(config_obj),'-o',str(selected)],check=True);u,d=undefined_symbols(selected);assert not u,u
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,object_transforms=[transform,['arm-none-eabi-objcopy','--strip-unneeded',str(obj)]],compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,sdk_report_sha256=sha(sp),selected_object_sha256=sha(selected),configuration_source=str(config_source.relative_to(ROOT)),configuration_command=config_cmd,configuration_object_sha256=sha(config_obj),remaining_symbols=u,configuration={'NRFX_CLOCK_CONFIG_LF_SRC':0,'NRFX_CLOCK_CONFIG_LF_CAL_ENABLED':1,'NRFX_CLOCK_CONFIG_IRQ_PRIORITY':6,'NRF_ASSERT_PRESENT':0},scope='Pinned nrfx clock init/enable/LF-start/LF-stop and IRQ dispatcher with actual HAL/NVIC helpers, plus source-owned IRQ0 vector word; calibration-state byte enabled and assertions disabled by local native contract; O0 preserves the single native control block instead of Clang scalar splitting',instruction_identity_proven=False),indent=2)+'\n');print('Pinned nrfx clock hardware compiled with no unresolved providers')
if __name__=='__main__':main()

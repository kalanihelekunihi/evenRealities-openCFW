#!/usr/bin/env python3
"""Compile the unchanged authenticated SDK example's buttonless-DFU state callback."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'sdk-dfu-state';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());row=next(x for x in sdk['units'] if x['source'].endswith('/ble_dfu.c'));flags=row['command'][1:row['command'].index('-c')];sdkroot=ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560';source=sdkroot/'examples/ble_peripheral/ble_app_buttonless_dfu/main.c';rawtext=source.read_bytes();start=rawtext.index(b'static void buttonless_dfu_sdh_state_observer(');end=rawtext.index(b'\r\n}\r\n',start)+5;body=rawtext[start:end];generated=out/'dfu-state-from-sdk.c';generated.write_bytes(b'#include "nrf_sdh.h"\n#include "nrf_power.h"\n#include "nrf_pwr_mgmt.h"\n#include "nrf_bootloader_info.h"\n'+body+b'\nvoid (*const r1_dfu_state_compile_anchor)(nrf_sdh_state_evt_t,void *)=buttonless_dfu_sdh_state_observer;\n');raw=out/'dfu-state-raw.o';obj=out/'dfu-state.o';dep=out/'dfu-state.d';cmd=['clang',*flags,'-I'+str(sdkroot/'components/libraries/bootloader'),'-MD','-MF',str(dep),'-c',str(generated),'-o',str(raw)];subprocess.run(cmd,check=True)
 transform=['arm-none-eabi-objcopy','--redefine-sym','buttonless_dfu_sdh_state_observer=r1_sdh_state_observer_567ac','--globalize-symbol=r1_sdh_state_observer_567ac',str(raw)];subprocess.run(transform,check=True);link=['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_sdh_state_observer_567ac',str(raw),'-o',str(obj)];subprocess.run(link,check=True);strip=['arm-none-eabi-objcopy','--strip-unneeded',str(obj)];subprocess.run(strip,check=True);inputs={str(source.relative_to(ROOT)):sha(source)}
 for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 u,d=undefined_symbols(obj);assert u==['nrf_pwr_mgmt_shutdown'],u
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,object_transforms=[transform,strip],compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,sdk_report_sha256=sha(sp),selected_object_sha256=sha(obj),remaining_symbols=u,extraction={'offset':start,'length':len(body),'sha256':hashlib.sha256(body).hexdigest(),'generated_source':str(generated.relative_to(ROOT)),'generated_sha256':sha(generated),'compile_anchor_selected':False},scope='Exact unchanged SDK example callback slice, official SDK headers/macros and private-symbol alias; unrelated main/example code excluded and compile anchor discarded',instruction_identity_proven=False),indent=2)+'\n');print('Pinned DFU state callback compiled; remaining: nrf_pwr_mgmt_shutdown')
if __name__=='__main__':main()

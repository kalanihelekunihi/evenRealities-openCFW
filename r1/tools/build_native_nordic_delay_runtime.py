#!/usr/bin/env python3
"""Compile unchanged pinned Nordic delay loop and reuse source cycle primitive."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-nordic-delay-runtime';out.mkdir(exist_ok=True);source=ROOT/'r1/components/runtime/native_nordic_delay.c';obj=out/'native_nordic_delay.o';dep=out/'native_nordic_delay.d';sdk=ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560';header=sdk/'components/libraries/delay/nrf_delay.h';archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as z:assert hashlib.sha256(z.read(str(header.relative_to(sdk.parent)))).hexdigest()==sha(header)
 cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-fshort-enums','-std=c11','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(ROOT/'r1/source-config/runtime/nordic-delay'),'-I'+str(header.parent),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
 inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),str((sdk/'modules/nrfx/soc/nrfx_coredep.h').relative_to(ROOT)):sha(sdk/'modules/nrfx/soc/nrfx_coredep.h')}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(p);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
 parent=BASE/'native-battery-kv-runtime/native-battery-kv-runtime.o';rp=parent.parent/'report.json';r=json.loads(rp.read_text());assert sha(parent)==r['linked_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 primitive=out/'delay-primitive-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_rtt_delay_cycles',str(parent),'-o',str(primitive)],check=True)
 small=out/'nordic-delay-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(obj),str(primitive),'-o',str(small)],check=True);assert not undefined_symbols(small)[0]
 linked=out/'native-nordic-delay-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(obj),str(parent),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(r['undefined_symbols']);assert old-set(u)=={'nrf_delay_ms'} and not set(u)-old
 unit=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0])
 report=dict(units=[unit],inputs=inputs,provider_reports={str(rp.relative_to(BASE)):sha(rp),'native-rtt-delay/report.json':sha(BASE/'native-rtt-delay/report.json')},objects={str(parent.relative_to(BASE)):sha(parent)},primitive_object_sha256=sha(primitive),delay_object_sha256=sha(small),linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=['nrf_delay_ms'],newly_exposed_imports=[],unchanged_sdk_delay_header=True,cycle_conversion=64,hardware_elapsed_time_verified=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Nordic delay SDK source linked;',len(u),'imports')
if __name__=='__main__':main()

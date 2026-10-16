#!/usr/bin/env python3
"""Compile explicit ARM delay primitive from attributable SDK instruction contract."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-rtt-delay';out.mkdir(exist_ok=True);source=ROOT/'r1/components/board/native_rtt_delay.c';obj=out/'rtt-delay.o';dep=out/'delay.d';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);u,d=undefined_symbols(obj);assert not u,u
 inputs={str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else p:sha(Path(p)) for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split()};header=ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/modules/nrfx/soc/nrfx_coredep.h';archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/modules/nrfx/soc/nrfx_coredep.h')).hexdigest()==sha(header)
 inputs[str(header.relative_to(ROOT))]=sha(header);raw=header.read_bytes();a=raw.index(b'    // Align the machine code');b=raw.index(b'    typedef void (* delay_func_t)',a);(out/'sdk-instruction-contract.txt').write_bytes(raw[a:b]);row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u);(out/'report.json').write_text(json.dumps(dict(units=[row],inputs=inputs,selected_object_sha256=sha(obj),remaining_symbols=u,sdk_instruction_contract_sha256=sha(out/'sdk-instruction-contract.txt'),scope='Compiler-supported three-mnemonic ARM delay primitive; standalone body identity and hardware timing require separate verification',instruction_identity_proven=False),indent=2)+'\n');print('ARM delay primitive compiled; no unresolved providers')
if __name__=='__main__':main()

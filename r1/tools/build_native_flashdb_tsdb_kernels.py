#!/usr/bin/env python3
"""Compile attributable FlashDB helpers; no promotion into main ABI graph."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 out=ROOT/'r1/research/source-build/native-flashdb-tsdb-kernels';out.mkdir(exist_ok=True)
 source=ROOT/'r1/components/runtime/native_flashdb_tsdb_kernels.c';obj=out/'native_flashdb_tsdb_kernels.o'
 command=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-std=c11','-ffreestanding','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-isystem','vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include','-I','r1/config-recovered','-I','third-party/upstream/flashdb-2.0.0/inc','-I','third-party/upstream/flashdb-2.0.0/port/fal/inc','-c',str(source.relative_to(ROOT)),'-o',str(obj.relative_to(ROOT))]
 subprocess.run(command,cwd=ROOT,check=True)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 report=dict(command=command,source_sha256=sha(source),object_sha256=sha(obj),upstream_slices_sha256=sha(out/'upstream-slices.json'),compiler=subprocess.check_output(['clang','--version'],text=True).splitlines()[0],upstream_pin=subprocess.check_output(['git','-C',str(ROOT/'third-party/upstream/flashdb-2.0.0'),'rev-parse','HEAD'],text=True).strip(),license='Apache-2.0',raw_abi_gate_open=True,main_provider_graph_linked=False,whole_image_complete=False)
 (out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()

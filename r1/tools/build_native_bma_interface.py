#!/usr/bin/env python3
"""Compile native Bosch interface/configuration with attributable pinned API layout."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-bma-interface';out.mkdir(exist_ok=True);vendor=ROOT/'third-party/upstream/bosch-bma456'
 # Existing sensor receipt authenticates this exact pinned primary-source checkout.
 expected={'bma4.c':'bb2dc4a7a75774f38d39ec9242fdba1f9fc7e1a66dc6c0e8767f776e3683013d','bma4.h':'79a5f967938d50acfeaa096f65759c2d9156a38f153f85800bf3b4dae25e1ef4','bma4_defs.h':'b0bf49bc03c12ef94d01cc0ba43f13ba0ba127204b707b211b6559d4d1b2d9ae','LICENSE':'7d32b0d25c587b4a9c25adb882885fe63ce77533d90f26676d2edf40f5b302c9'}
 for name,h in expected.items():assert sha(vendor/name)==h,name
 raw=(vendor/'bma4.c').read_bytes().decode();m=re.search(r'static int8_t null_pointer_check\(const struct bma4_dev \*dev\)\r?\n\{.*?\r?\n\}',raw,re.S);assert m;body=m.group();generated=out/'bosch-null-check.c';generated.write_text('/* Attributed Bosch helper: rename/export only.\n'+(vendor/'LICENSE').read_text()+'\n*/\n#include "bma4.h"\n'+body.replace('static int8_t null_pointer_check','int8_t r1_bma4_null_pointer_check',1)+'\n')
 parent=BASE/'native-lis-aux';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs']);inputs.update({str((vendor/name).relative_to(ROOT)):h for name,h in expected.items()});inputs[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 rows=[];objects=[]
 for source,name in [(ROOT/'r1/components/runtime/native_bma_interface.c','native_bma_interface.o'),(generated,'bosch-null-check.o')]:
  obj=out/name;cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=hard','-mfpu=fpv4-sp-d16','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(vendor),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs[str(source.relative_to(ROOT))]=sha(source);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0]));objects.append(obj)
 po=parent/'native-lis-aux-runtime.o';assert sha(po)==p['linked_sha256'];linked=out/'native-bma-interface-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),*map(str,objects),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];assert u==p['undefined_symbols'] and len(u)==26
 roots=['r1_bma_interface_initialize','r1_bma_default_read','r1_bma_default_write','r1_bma_delay_us','r1_bma4_null_pointer_check','r1_bma_context'];graph=out/'interface-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for x in roots for v in ['-u',x]],str(linked),'-o',str(graph)],check=True);assert not undefined_symbols(graph)[0]
 r=dict(units=rows,inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,roots=roots,upstream_pin='3266db2c5de15be1a00232b8c0f2fd23e07934e0',upstream_license='BSD-3-Clause',upstream_function='null_pointer_check',source_slice_start=m.start(),source_slice_end=m.end(),original_slice_sha256=hashlib.sha256(body.encode()).hexdigest(),adaptation='Rename/export static helper only; typed pinned header layout asserted',pinned_context_type_bytes=52,full_native_context_extent_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Native BMA interface + attributed null check compiled; selected graph zero imports; main26 imports')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Compile LIS configuration provider and compose with authenticated parent."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-lis-configure';out.mkdir(exist_ok=True);src=ROOT/'r1/components/runtime/native_lis_configure.c';obj=out/'native_lis_configure.o'
 cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=hard','-mfpu=fpv4-sp-d16','-std=c11','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fshort-enums','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 parent=BASE/'native-lis-setup';pr=parent/'report.json';p=json.loads(pr.read_text());po=parent/'native-lis-setup-runtime.o';assert sha(po)==p['linked_sha256']
 inputs=dict(p['inputs']);inputs.update({str(src.relative_to(ROOT)):sha(src),str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))})
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 linked=out/'native-lis-configure-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];assert set(p['undefined_symbols'])-set(u)=={'r1_lis2dw12_configure_boundary'} and not set(u)-set(p['undefined_symbols']) and len(u)==28
 roots=['r1_lis2dw12_configure_boundary'];graph=out/'configure-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for x in roots for v in ['-u',x]],str(linked),'-o',str(graph)],check=True)
 r=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),source_sha256=sha(src),unit_object_sha256=sha(obj),command=cmd,linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=['r1_lis2dw12_configure_boundary'],newly_exposed_imports=[],whole_image_complete=False,instruction_identity=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('LIS configuration provider compiled:28 main imports; logging dependencies remain in selected graph')
if __name__=='__main__':main()

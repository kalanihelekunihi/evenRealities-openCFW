#!/usr/bin/env python3
"""Compile two attributed ST multi-register bodies and two native setup contracts."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={0x75120:'lis2dw12_data_rate_set',0x75450:'lis2dw12_filter_path_set',0x7575a:'r1_lis_native_power_mode_set',0x7518a:'r1_lis_reg17_bit6_enable'}
def main():
 out=BASE/'native-lis-setup';out.mkdir(exist_ok=True);vendor=ROOT/'vendor-cache/r1/st-lis2dw12-8d4bd522015004a9646102702901ba5a15ec6d39';raw=(vendor/'lis2dw12_reg.c').read_bytes().decode();parent=BASE/'native-lis-registers';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 bodies=[];slices=[]
 for name,locals_ in [('lis2dw12_data_rate_set',['ctrl1','ctrl3']),('lis2dw12_filter_path_set',['ctrl6','ctrl_reg7'])]:
  m=re.search(r'int32_t '+name+r'\(.*?\r?\n\}',raw,re.S);assert m;body=m.group();adapted=body.replace(name+'(',name+'_body(',1);pos=adapted.index(')');adapted=adapted[:pos]+', volatile uint8_t *frame'+adapted[pos:]
  for i,local in enumerate(locals_):
   localmatch=re.search(r'  (lis2dw12_\w+_t) '+local+';',adapted);assert localmatch;adapted=adapted.replace(localmatch.group(),f'  {localmatch[1]} *{local}=({localmatch[1]} *)(uintptr_t)(frame+{4*i});').replace('(uint8_t *) &'+local,'(uint8_t *)'+local).replace(local+'.',local+'->')
  bodies.append(adapted);slices.append(dict(name=name,start=m.start(),end=m.end(),original_slice_sha256=hashlib.sha256(body.encode()).hexdigest(),adaptations=['Rename internal kernel and append explicit frame','Externalize two local register bytes at native frame offsets0 and4','Redirect pointers/member accesses; preserve algorithm and status gates']))
 generated=out/'st-setup-frames.c';generated.write_text('/* Attributed ST frame adaptation.\n'+(vendor/'LICENSE').read_text()+'\n*/\n#include <stdint.h>\n#include "lis2dw12_reg.h"\n'+'\n'.join(bodies)+'\n');src=ROOT/'r1/components/runtime/native_lis_setup.c';inputs[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__));rows=[];objects=[]
 for source,name in [(src,'native_lis_setup.o'),(generated,'st-setup-frames.o')]:
  obj=out/name;cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=hard','-mfpu=fpv4-sp-d16','-std=c11','-Os','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(vendor),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs[str(source.relative_to(ROOT))]=sha(source);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0]));objects.append(obj)
 po=parent/'native-lis-registers-runtime.o';assert sha(po)==p['linked_sha256'];linked=out/'native-lis-setup-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),*map(str,objects),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];assert u==p['undefined_symbols'] and len(u)==29
 graph=out/'setup-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for x in ENTRIES.values() for v in ['-u',x]],str(linked),'-o',str(graph)],check=True);assert not undefined_symbols(graph)[0]
 r=dict(units=rows,inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,source_slices=slices,upstream_pin='8d4bd522015004a9646102702901ba5a15ec6d39',upstream_license='BSD-3-Clause',exact_vendor_checkout_proven=False,native_power_enum_matches_modern_st=False,native_second_read_error_still_writes_and_adds_status=True,reg17_semantic_name_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('LIS multi-register setup compiled; selected graph zero imports; main29 imports')
if __name__=='__main__':main()

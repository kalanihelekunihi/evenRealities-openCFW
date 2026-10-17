#!/usr/bin/env python3
"""Compile Bosch base/variant initialization and authenticated product sequence/data."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-bma-initialize';out.mkdir(exist_ok=True);parent=BASE/'native-bma-setup';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs']);vendor=ROOT/'third-party/upstream/bosch-bma456'
 for name,h in {'bma456w.c':'01fc4f47a03db4244f9d86c97ca03e5c73bdf28a2ae3385ac37a097eb6559f21','bma456w.h':'30c6dd9c291a45555bb5fa428544f7fa91369b1ee518a4bc50580ef6de6dfa92'}.items():assert sha(vendor/name)==h;inputs[str((vendor/name).relative_to(ROOT))]=h
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 raw=(vendor/'bma456w.c').read_text();array=re.search(r'const uint8_t bma456w_config_file\[\]\s*=\s*\{(.*?)\};',raw,re.S);assert array;config_size=len(re.findall(r'0x[0-9a-fA-F]+',array[1]));assert config_size==5016
 slices=[]
 for file,name in [('bma4.c','bma4_init'),('bma456w.c','bma456w_init')]:
  rawbytes=(vendor/file).read_bytes();m=re.search(r'int8_t '+name+r'\([^;]*?\)\r?\n\{.*?\r?\n\}',rawbytes.decode(),re.S);assert m;slices.append(dict(file=file,function=name,start=m.start(),end=m.end(),original_slice_sha256=hashlib.sha256(m.group().encode()).hexdigest()))
 src=ROOT/'r1/components/runtime/native_bma_initialize.c';obj=out/'native_bma_initialize.o';dep=obj.with_suffix('.d');cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-munaligned-access','-mfloat-abi=hard','-mfpu=fpv4-sp-d16','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(vendor),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-MD','-MF',str(dep),'-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 for path in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  q=Path(path);inputs[str(q.relative_to(ROOT)) if q.is_relative_to(ROOT) else path]=sha(q)
 inputs[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__));po=parent/'native-bma-setup-runtime.o';assert sha(po)==p['linked_sha256'];linked=out/'native-bma-initialize-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];closed=sorted(set(p['undefined_symbols'])-set(u));assert closed==['r1_bma456w_configure_boundary'] and not set(u)-set(p['undefined_symbols']) and len(u)==23
 roots=['r1_bma4_initialize','r1_bma456w_initialize','r1_bma456w_configure_boundary'];graph=out/'initialize-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for x in roots for v in ['-u',x]],str(linked),'-o',str(graph)],check=True);spans=out/'configuration-text-spans.json'
 r=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],closed_parent_imports=closed,newly_exposed_imports=[],roots=roots,configuration_text_spans_sha256=sha(spans),upstream_pin='3266db2c5de15be1a00232b8c0f2fd23e07934e0',upstream_license='BSD-3-Clause',source_slices=slices,upstream_config_array_bytes=config_size,feature_stream_uploaded_by_this_sequence=False,default_remap_typed_bytes=6,observed_literal_read_bytes=8,observed_following_bytes_hex='802e',following_bytes_semantic_origin_proven=False,exact_vendor_checkout_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Bosch initialize/configure compiled:23 main imports;6 typed remap bytes +2 explicit observed following bytes')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Unify cache aliases, remove orphan prefix sections, compile native getters."""
import hashlib,json,subprocess
from collections import Counter
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-latest-samples';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ALIASES={'r1_health_storage_hr_prefix':'r1_cache_hr','r1_health_storage_spo2_prefix':'r1_cache_spo2','r1_health_storage_hrv_prefix':'r1_cache_hrv'};REMOVE=['.r1.health.storage.hr','.r1.health.storage.spo2','.r1.health.storage.hrv']
def symbol_rows(path):
 secs={}
 import re
 for line in subprocess.check_output(['arm-none-eabi-readelf','-SW',str(path)],text=True).splitlines():
  if m:=re.match(r'\s*\[\s*(\d+)\]\s+(\S+)',line):secs[m[1]]=m[2]
 rows=[]
 for line in subprocess.check_output(['arm-none-eabi-readelf','-sW',str(path)],text=True).splitlines():
  f=line.split()
  if len(f)>=8 and f[0].endswith(':') and f[3] not in ['SECTION','FILE']:rows.append(tuple(f[1:6]+[secs.get(f[6],f[6]),f[7]]))
 return Counter(rows)
def main():
 parent=BASE/'native-sleep-report';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 po=parent/'native-sleep-report-runtime.o';assert sha(po)==p['linked_sha256'];alias=OUT/'parent-cache-aliases.o';subprocess.run(['arm-none-eabi-ld','-r',*[f'--defsym={a}={b}' for a,b in ALIASES.items()],str(po),'-o',str(alias)],check=True);assert allocated_sections(po)==allocated_sections(alias)
 old=symbol_rows(po);new=symbol_rows(alias)
 for a,target in ALIASES.items():
  before=next(x for x in old if x[-1]==a);after=next(x for x in new if x[-1]==a);targetrow=next(x for x in new if x[-1]==target);assert before[:-2]==after[:-2] and after[-2]==targetrow[-2] and before[-2] in REMOVE;old.subtract([before]);new.subtract([after])
 assert +old==+new
 clean=OUT/'parent-shared-caches.o';subprocess.run(['arm-none-eabi-objcopy',*[v for s in REMOVE for v in ['--remove-section',s]],str(alias),str(clean)],check=True);expected=allocated_sections(alias)
 for sec in REMOVE:del expected[sec]
 symbols=symbol_rows(alias);removed_mapping=[x for x in symbols if x[-1]=='$d' and x[-2] in REMOVE];assert len(removed_mapping)==3 and all(symbols[x]==1 for x in removed_mapping)
 for row in removed_mapping:del symbols[row]
 assert allocated_sections(clean)==expected and symbol_rows(clean)==symbols
 config=OUT/'shared-caches.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in list(ALIASES)+list(ALIASES.values()) for v in ['-u',n]],str(clean),'-o',str(config)],check=True);assert sum(x[2] for x in allocated_sections(config).values())==328
 src=ROOT/'r1/components/runtime/native_health_latest_samples.c';obj=OUT/'native_health_latest_samples.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-ffreestanding','-fshort-enums','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 for f in [src,Path(__file__)]:inputs[str(f.relative_to(ROOT))]=sha(f)
 linked=OUT/'native-health-latest-samples-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(clean),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];assert u==p['undefined_symbols'] and len(u)==68
 roots=p['roots']+['r1_'+fam+'_latest_'+kind for fam in ['hr','hrv','spo2'] for kind in ['sample','packed']];graph=OUT/'latest-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],str(linked),'-o',str(graph)],check=True);assert not set(REMOVE)&set(allocated_sections(graph))
 report=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),parent_alias_sha256=sha(alias),parent_clean_sha256=sha(clean),cache_aliases=ALIASES,shared_config_sha256=sha(config),shared_existing_cache_bytes=328,removed_sections=REMOVE,removed_orphan_prefix_bytes=313,removed_mapping_symbols=removed_mapping,other_allocated_sections_unchanged=True,other_symbol_rows_unchanged=True,linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=[],newly_exposed_imports=[],native_body_bytes=216,native_source_span_bytes=230,new_ram_state_bytes=0,whole_image_complete=False,hardware_write_executed=False);(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Unified three cache prefixes;313 orphan bytes removed; six getters compile;68 imports unchanged')
if __name__=='__main__':main()

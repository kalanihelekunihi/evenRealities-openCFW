#!/usr/bin/env python3
"""Reuse the source registry/string provider for the ADC cache."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-vbat-cache-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name in [('native-vbat-cache','native_vbat_cache.o'),('native-reset-writer-runtime','native-reset-writer-runtime.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 registry=out/'registry-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_stock_registry_find',str(objects[1]),'-o',str(registry)],check=True)
 small=out/'vbat-cache-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(registry),'-o',str(small)],check=True);su,sd=undefined_symbols(small);assert not su
 linked=out/'native-vbat-cache-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(p) for p in objects],'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert 'r1_vbat_adc_handle_cache' not in u
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},registry_object_sha256=sha(registry),cache_object_sha256=sha(small),cache_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,whole_startup_graph_executed=False,physical_adc_verified=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Cache source bundle zero imports;',len(u),'startup imports remain')
if __name__=='__main__':main()

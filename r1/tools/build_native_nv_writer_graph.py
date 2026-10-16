#!/usr/bin/env python3
"""Compose actual class serializer/CRC with NV update and scan callers."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-nv-class-writer-runtime';inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for name,filename,key in [('native-nv-class-writer','native_nv_class_writer.o',None),('native-nv-update-runtime','nv-update-source.o','graph_object_sha256'),('native-nv-class-writer-runtime','writer-helpers-source.o','helper_object_sha256')]:
  rp=BASE/name/'report.json';r=json.loads(rp.read_text());obj=rp.parent/filename;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 crc=out/'writer-crc-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_stock_crc16_modbus',str(objects.pop()),'-o',str(crc)],check=True);objects.append(crc)
 graph=out/'nv-writer-graph-source.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(graph)],check=True);u,d=undefined_symbols(graph)
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},graph_object_sha256=sha(graph),undefined_symbols=u,whole_flash_commit_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'caller-graph-report.json').write_text(json.dumps(r,indent=2)+'\n');print('NV writer graph providers:',u)
if __name__=='__main__':main()

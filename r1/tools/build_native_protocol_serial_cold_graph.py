#!/usr/bin/env python3
"""Select existing cached-class reader for the source-owned serial class graph."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-serial-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());raw=BASE/'native-protocol-serial/native_protocol_serial.o';rr=BASE/'native-protocol-serial/report.json';assert sha(raw)==json.loads(rr.read_text())['units'][0]['object_sha256'];kr=BASE/'native-kv-class/report.json';k=json.loads(kr.read_text());ko=Path(k['units'][0]['command'][-1]);assert sha(ko)==k['units'][0]['object_sha256'];memory=OUT/'serial-memory-source.o';assert sha(memory)==r['memory_object_sha256']
 inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for q in [r,k]:
  for p,h in q['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 selected=OUT/'kv-class-read-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_kv_class_read',str(ko),'-o',str(selected)],check=True)
 obj=OUT/'serial-cold-class-graph-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(raw),str(memory),str(selected),'-o',str(obj)],check=True);u,d=undefined_symbols(obj);assert u==['r1_kv_port','r1_protocol_send_response']
 report=dict(inputs=inputs,provider_reports={str(p.relative_to(BASE)):sha(p) for p in [rp,rr,kr]},objects={str(p.relative_to(BASE)):sha(p) for p in [raw,memory,ko]},selected_object_sha256=sha(selected),graph_object_sha256=sha(obj),undefined_symbols=u,whole_kv_flash_or_transport_executed=False,whole_image_complete=False)
 (OUT/'cold-graph-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Serial graph uses actual cached-class/memory/header/read source;port and transport seams remain')
if __name__=='__main__':main()

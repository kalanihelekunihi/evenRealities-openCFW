#!/usr/bin/env python3
"""Compose actual role body, status ring and shared connection cells."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-status-ring-runtime';objects=[BASE/'native-phone-role/native_phone_role.o',out/'status-ring-source.o'];reports=[BASE/'native-phone-role/report.json',out/'report.json'];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for rp in reports:
  r=json.loads(rp.read_text())
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 assert sha(objects[0])==json.loads(reports[0].read_text())['units'][0]['object_sha256'] and sha(objects[1])==json.loads(reports[1].read_text())['status_object_sha256']
 graph=out/'role-status-graph-source.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(graph)],check=True);u,d=undefined_symbols(graph)
 report=dict(inputs=inputs,provider_reports={str(p.relative_to(BASE)):sha(p) for p in reports},objects={str(p.relative_to(BASE)):sha(p) for p in objects},graph_object_sha256=sha(graph),undefined_symbols=u,whole_battery_event_or_rtos_graph_executed=False,whole_image_complete=False)
 (out/'role-graph-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Role/status graph imports:',u)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Compose protocol control with the actual BLE encoder and source memory copy."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-ble-message-runtime';objects=[BASE/'native-protocol-control-runtime/protocol-control-source.o',BASE/'native-ble-message/native_ble_message.o'];reports=[BASE/'native-protocol-control-runtime/report.json',BASE/'native-ble-message/report.json',out/'report.json'];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for rp in reports:
  r=json.loads(rp.read_text())
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 assert sha(objects[0])==json.loads(reports[0].read_text())['control_object_sha256'] and sha(objects[1])==json.loads(reports[1].read_text())['units'][0]['object_sha256']
 helper=out/'message-copy-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_native_memory_move',str(out/'message-helpers-source.o'),'-o',str(helper)],check=True);objects.append(helper)
 graph=out/'ble-control-graph-source.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(graph)],check=True);u,d=undefined_symbols(graph)
 report=dict(inputs=inputs,provider_reports={str(p.relative_to(BASE)):sha(p) for p in reports},objects={str(p.relative_to(BASE)):sha(p) for p in objects},graph_object_sha256=sha(graph),undefined_symbols=u,whole_allocator_queue_or_rtos_graph_executed=False,whole_image_complete=False)
 (out/'control-graph-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BLE control graph imports:',u)
if __name__=='__main__':main()

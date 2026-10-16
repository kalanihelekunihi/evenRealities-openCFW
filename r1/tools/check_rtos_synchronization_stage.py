#!/usr/bin/env python3
"""Compose source-owned synchronization providers without frontier promotion."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 board_report=BASE/'board/report.json';board=json.loads(board_report.read_text());board_obj=BASE/'board/native-board.o';assert sha(board_obj)==board['relocatable_sha256'];objects=[board_obj];reports={};receipts={};evidence={};board_objects=set(board['objects'])
 for name,objname,count in [('rtos-synchronization','synchronization.o',18192),('rtos-mutex-kernel','mutex-kernel.o',5562),('rtos-mutex-tasks','mutex-tasks.o',5162)]:
  folder=BASE/name;rp=folder/'report.json';r=json.loads(rp.read_text());obj=folder/objname;assert sha(obj)==r['selected_object_sha256'];
  if str(obj.relative_to(ROOT)) not in board_objects:objects.append(obj)
  reports[name+'/report.json']=sha(rp);assert r['rtos_report_sha256']==sha(BASE/'rtos/report.json')
  for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
  raw=(ROOT/r['upstream_source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['upstream_sha256'];text=raw.decode()
  for row in r['source_slices']:assert hashlib.sha256(text[row['start']:row['end']].encode()).hexdigest()==row['sha256'],row['name']
  if count is not None:
   vp=folder/'verification.json';v=json.loads(vp.read_text());assert v['application_sha256']==sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin') and v['report_sha256']==sha(rp) and v['driver_sha256']==sha(ROOT/'r1/tools'/('verify_'+name.replace('-','_')+'.py')) and v['comparisons']==count;receipts[name+'/verification.json']=sha(vp)
  ep=folder/'evidence.json';e=json.loads(ep.read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert e['application_sha256']==sha(app) and e['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
  for span in e['spans']:
   p=folder/span['ghidra_file'];a=int(span['entry'],16);assert sha(p)==span['ghidra_sha256'] and bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+span['bytes']]
  assert sha(ROOT/e['rea_inventory'])==e['rea_inventory_sha256'];evidence[name+'/evidence.json']=sha(ep)
 out=BASE/'rtos-synchronization/synchronization-stage.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(out)],check=True);before=set(undefined_symbols(board_obj)[0]);after=set(undefined_symbols(out)[0]);assert not after-before,sorted(after-before)
 result=dict(driver_sha256=sha(Path(__file__)),board_report_sha256=sha(board_report),board_object_sha256=sha(board_obj),provider_reports=reports,isolated_receipts=receipts,evidence=evidence,selected_object_sha256=sha(out),comparisons=28916,resolved_board_symbols=sorted(before-after),new_unresolved_symbols=sorted(after-before),compiled_unverified_modules=[],canonical_board_includes_synchronization_objects=all(str(p.relative_to(ROOT)) in board_objects for p in (BASE/'rtos-synchronization/synchronization.o',BASE/'rtos-mutex-kernel/mutex-kernel.o',BASE/'rtos-mutex-tasks/mutex-tasks.o')),frontier_promoted_by_this_check=False,combined_graph_verified=False,byte_identity=False,limitations=['All selected bodies have isolated native receipts. This check establishes relocatable source composition only; the synchronization graph and canonical audit are separate checks. No physical/runtime/whole-image proof.']);(out.parent/'stage-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['comparisons'],'isolated comparisons; source stage resolves:',result['resolved_board_symbols'],'without adding unresolved symbols')
if __name__=='__main__':main()

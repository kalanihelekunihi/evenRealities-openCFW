#!/usr/bin/env python3
"""Stage typed STACMD operations against the canonical source-owned registration/providers."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-stacmd-stage';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=True);receipt=OUT/'verification.json';receipt.unlink(missing_ok=True)
 board_report=BASE/'board/report.json';board=json.loads(board_report.read_text());board_object=BASE/'board/native-board.o';assert sha(board_object)==board['relocatable_sha256'];objects=[board_object];reports={'board/report.json':sha(board_report)}
 header=ROOT/'r1/components/board/native_stacmd.h';header_hash=sha(header)
 registration=BASE/'native-stacmd-registration/report.json';assert json.loads(registration.read_text())['inputs']['r1/components/board/native_stacmd.h']==header_hash
 for module in ('operations','recovery','transmit','receive','frames','delay','write-retry','state'):
  directory=BASE/('native-stacmd-'+module);report=directory/'report.json';r=json.loads(report.read_text());obj=directory/('native_stacmd_'+module.replace('-','_')+'.o');assert sha(obj)==r['units'][0]['object_sha256']
  assert r['inputs']['r1/components/board/native_stacmd.h']==header_hash
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
  if str(obj.relative_to(ROOT)) not in board['objects']:objects.append(obj)
  reports[str(report.relative_to(BASE))]=sha(report)
 obj=OUT/'stacmd-stage.o';command=['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(obj)];subprocess.run(command,check=True,capture_output=True)
 remaining,defined=undefined_symbols(obj);closed={'r1_stacmd_open','r1_stacmd_close','r1_stacmd_read','r1_stacmd_write'};expected=set(board['remaining_symbols'])-closed
 assert set(remaining)==expected and closed.issubset(defined) and {'r1_stacmd','r1_stacmd_failed_transactions'}.issubset(defined)
 nm=subprocess.check_output(['arm-none-eabi-nm',str(obj)],text=True);assert sum(line.split()[-1]=='r1_stacmd' and len(line.split())==3 for line in nm.splitlines())==1
 state_receipt=BASE/'native-stacmd-state/verification.json';state=json.loads(state_receipt.read_text());assert state['object_sha256']==sha(BASE/'native-stacmd-state/native_stacmd_state.o') and state['comparisons']==4
 assert sum(line.split()[-1]=='r1_stacmd_failed_transactions' and len(line.split())==3 for line in nm.splitlines())==1
 receipt.write_text(json.dumps(dict(state_verification_sha256=sha(state_receipt),board_report_sha256=sha(board_report),board_object_sha256=sha(board_object),provider_reports=reports,objects={str(p.relative_to(ROOT)):sha(p) for p in objects},shared_header_sha256=header_hash,registration_report_sha256=sha(registration),stage_object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),remaining_symbols=remaining,closed_board_operation_providers=sorted(closed),new_unresolved_data=[],source_owned_configuration='Exactly one r1_stacmd definition from canonical registration and one source-owned cold-zero counter',canonical_board_integrated=len(objects)==1,application_linked=False,instruction_identity=False,limitations=['Relocatable stage closes four operation providers using canonical source-owned configuration and providers; no executable stage runtime receipt yet','Cold counter initializer is verified; warm-reset lifecycle and whole startup remain separate gates','Existing board unresolved symbols and startup/original instruction/byte identity remain open','Physical GPIO return/timing/concurrency and complete transport composition remain gates']),indent=2)+'\n');print('STACMD stage:',len(remaining),'unresolved symbols; four operation providers closed and cold counter source-owned')
if __name__=='__main__':main()

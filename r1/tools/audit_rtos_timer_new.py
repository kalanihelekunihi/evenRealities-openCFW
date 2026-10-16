#!/usr/bin/env python3
"""Reconstruct and authenticate pinned CMSIS creation/callback and native timer-ID getter."""
import hashlib,json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 out=BASE/'rtos-timer-new';v=json.loads((out/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert v['counts']=={'osTimerNew':4752,'TimerCallback':16,'pvTimerGetTimerID':10} and v['comparisons']==4778 and v['assertion_or_null_callback_faults']==15
 assert v['application_sha256']==sha(app) and v['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_timer_new.py') and not v['application_linked'] and not v['instruction_identity']
 for module,stem,header in [('rtos-timer-new','timer-new','timer_new_contract.h'),('rtos-timer-id','timer-id','timer_id_contract.h')]:
  rp=BASE/module/'report.json';r=json.loads(rp.read_text());assert sha(rp)==v['provider_reports'][module+'/report.json'];assert r['rtos_report_sha256']==sha(BASE/'rtos/report.json');up=ROOT/r['upstream_source'];assert sha(up)==r['upstream_sha256'];raw=up.read_bytes();parts=[]
  for s in r['source_slices']:
   part=raw[s['start']:s['end']];assert hashlib.sha256(part).hexdigest()==s['sha256'];parts.append(part)
  if module=='rtos-timer-new':parts=parts[:1]+list(reversed(parts[-2:]))+parts[1:-2]
  license=raw[:r['license_bytes']];assert hashlib.sha256(license).hexdigest()==r['license_sha256'];expected=license+b'\n#include "'+header.encode()+b'"\n'+b'\n'.join(parts)+r.get('generated_suffix','').encode();source=BASE/module/(stem+'.c');assert source.read_bytes()==expected
  unit=r['units'][0];assert sha(source)==unit['source_sha256'];assert sha(BASE/module/(stem+'.o'))==unit['object_sha256']==r['selected_object_sha256']
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 for filename,h in v['ghidra_evidence'].items():
  p=out/filename;assert sha(p)==h;n=filename.removeprefix('ghidra-').removesuffix('.json');a,z=v['entries'][n];assert bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+z]
 for filename,h in v['rea_evidence'].items():
  p=out/filename;assert sha(p)==h;assert json.loads(p.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
 p=out/'attribution-correction.json';assert sha(p)==v['attribution_correction_sha256'];e=json.loads(p.read_text());row=next(r for r in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if r['image']=='application' and r['entry']=='0x0008569c');assert e['original_row']==row and e['effective_symbol']=='pvTimerGetTimerID'
if __name__=='__main__':audit();print('Timer creation/callback/ID source and native evidence authenticated')

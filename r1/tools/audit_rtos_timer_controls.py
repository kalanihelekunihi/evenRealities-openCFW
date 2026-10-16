#!/usr/bin/env python3
"""Authenticate timer-control source slices, layouts and bounded native receipts."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 baseline=BASE/'rtos/report.json';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';r=json.loads((BASE/'rtos-timer-controls/verification.json').read_text())
 assert r['comparisons']==6784 and r['counts']=={'osTimerStart':2880,'osTimerStop':2880,'xTimerIsTimerActive':1024} and r['assertion_faults']==512
 assert r['application_sha256']==sha(app) and not r['application_linked'] and not r['instruction_identity']
 assert r['verifier_sha256']==sha(ROOT/'r1/tools/verify_rtos_timer_controls.py')
 for module,stem,header in [('rtos-timer-controls','timer-controls','timer_controls_contract.h'),('rtos-timer-active','timer-active','timer_active_contract.h')]:
  rp=BASE/module/'report.json';d=json.loads(rp.read_text());assert sha(rp)==r['provider_reports'][module+'/report.json'];assert sha(baseline)==d['rtos_report_sha256'];up=ROOT/d['upstream_source'];assert sha(up)==d['upstream_sha256'];raw=up.read_bytes();parts=[]
  for s in d['source_slices']:
   part=raw[s['start']:s['end']];assert hashlib.sha256(part).hexdigest()==s['sha256'];parts.append(part)
  if module=='rtos-timer-controls':parts=list(reversed(parts[-2:]))+parts[:-2]
  license=raw[:d['license_bytes']];assert hashlib.sha256(license).hexdigest()==d['license_sha256'];expected=license+b'\n#include "'+header.encode()+b'"\n'+b'\n'.join(parts)+d.get('generated_suffix','').encode();source=BASE/module/(stem+'.c');assert source.read_bytes()==expected
  unit=d['units'][0];assert sha(source)==unit['source_sha256'];assert sha(BASE/module/(stem+'.o'))==unit['object_sha256']==d['selected_object_sha256']
  for p,h in d['inputs'].items():assert sha(ROOT/p)==h,p
 for n,h in r['ghidra_evidence'].items():
  p=BASE/'rtos-timer-controls'/n;assert sha(p)==h;name=n.removeprefix('ghidra-').removesuffix('.json');address,length=r['entries'][name];assert bytes(json.loads(p.read_text())['data'])==app.read_bytes()[address-0x27000:address-0x27000+length]
 for n,h in r['rea_evidence'].items():
  p=BASE/'rtos-timer-controls'/n;assert sha(p)==h;v=json.loads(p.read_text());assert v['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
if __name__=='__main__':audit();print('Timer control source and native receipts authenticated')

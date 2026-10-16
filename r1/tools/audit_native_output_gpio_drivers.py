#!/usr/bin/env python3
"""Audit exact adapters separately from source provider and whole-image gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_native_output_gpio_runtime import ADAPTERS
 from build_source_candidates import undefined_symbols
 from audit_source_frontier import section_bytes
 out=BASE/'native-output-gpio-runtime';rp=out/'report.json';r=json.loads(rp.read_text())
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in r[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-output-gpio-runtime.o')==r['linked_sha256'] and undefined_symbols(out/'native-output-gpio-runtime.o')[0]==r['undefined_symbols'] and len(r['undefined_symbols'])==48
 assert sha(out/'adapters-native-placement.elf')==r['identity_elf_sha256'] and r['local_adapter_instruction_identity']
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for check in r['adapter_checks']:
  n=check['function'];a,p,t=ADAPTERS[n];data=out/(n+'.bin');assert data.read_bytes()==raw[a-0x27000:a-0x27000+6]==bytes.fromhex(check['bytes_hex']) and sha(data)==check['file_sha256'] and check['provider']==p and check['native_provider']==t
  # Read linked ELF anew, rather than trusting extracted files or report claims.
  assert section_bytes(out/'adapters-native-placement.elf','.text.'+n)==data.read_bytes()
 for a,length in [('54d8c',12),('54f3c',12),('54f8a',6)]:
  q=json.loads((BASE/'native-output-gpio-drivers'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==length and bytes.fromhex(d['bytes_hex'])==raw[i:i+length]
 assert r['closed_parent_imports']==sorted(ADAPTERS) and r['newly_exposed_imports']==[]
 for flag in ['provider_behavior_reverified','metadata_callback_abi_migrated','hardware_write_executed','whole_image_complete','instruction_identity']:assert not r[flag]
 print('Output GPIO: five exact six-byte adapters; pinned source provider reuse;48 imports;remaining operations/ABI/image gates open')
if __name__=='__main__':audit()

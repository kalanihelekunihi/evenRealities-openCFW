#!/usr/bin/env python3
"""Authenticate health-event consumer bodies, packed ABI and source callback composition."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-health-event-consumers';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';binary=app.read_bytes();assert sha(app)==r['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-event-callbacks';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-event-callbacks-runtime.o')==b['parent_object_sha256']
 assert sha(out/'native-health-event-consumers-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-health-event-consumers-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==57
 assert sha(out/'contracts.json')==b['contracts_sha256'] and len(c['units'])==6 and set(b['closed_parent_imports'])=={x['symbol'] for x in c['units']} and b['health_consumer_bodies_compiled']==6
 new={'r1_activity_event_storage','r1_hr_event_storage','r1_hrv_event_storage','r1_spo2_event_storage','r1_stress_event_storage','r1_temperature_event_storage','r1_health_event_notification_throttle'};assert set(b['newly_exposed_imports'])==new
 assert sha(out/'health-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'health-source.o')[0]==b['graph_undefined_symbols'] and set(b['graph_undefined_symbols'])==new and len(c['providers'])==8
 assert c['frozen_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')=='d7790642947403d713352d100e41a38c69b0619d6495aba3e1c47d6f02912968' and c['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and c['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and c['disassembly_sha256']==sha(out/'native-disassembly.txt') and not c['upstream_body_identity_proven']
 assert [(x['address'],x['size']) for x in c['units']]==[('0x8a7f4',22),('0x8a80a',52),('0x8a83e',40),('0x8a8ae',42),('0x8a8d8',36),('0x8a8fc',44)]
 source=(ROOT/b['units'][0]['source']).read_text()
 for x in c['units']:assert sum(v['size'] for v in x['instructions'])==x['size'] and 'void '+x['symbol']+'(uint32_t payload' in source and all('HEC_'+v['address'][2:]+':' in source for v in x['instructions'])
 assert sha(out/'rea-native-bytes.json')==r['rea_bytes_sha256'];n=json.loads((out/'rea-native-bytes.json').read_text())['structuredContent']['normalized_result'];assert n['complete'] and n['address']=='0x8a7f4' and n['returned_bytes']==308 and bytes.fromhex(n['bytes_hex'])==binary[0x8a7f4-0x27000:0x8a928-0x27000]
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_health_event_consumers.py')==r['driver_sha256'] and r['comparisons']==92320 and r['counts']==dict(direct=88288,callback_composed=4032,faults=720) and r['by_family']==dict(activity=1392,hr=7536,hrv=1392,spo2=7536,stress=7536,temperature=66928) and r['observation_counts']==dict(timestamp=10657,storage=14699,notify=11352,mode=1792,ring=448,sdk=448) and r['trace_sha256']=='a4b96f1ad2cc3be40ca6433d4500b13166f966c0c0ac703e458a0eda10d6f39c'
 for flag in ['all_65536_temperature_words_checked','packed_field_validation_and_timestamp_rules_independently_checked','actual_six_consumers_and_callbacks_execute','clock_storage_notification_and_log_are_fixtures']:assert r[flag]
 for flag in ['full_dispatcher_composition','full_private_frame_history_verified','full_raw_abi_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 fix=json.loads((out/'fixture-correction.json').read_text());assert fix['native_source_unchanged']
 for name,h in fix['preserved_files'].items():assert sha(out/'pre-storage-fixture-span-fix'/name)==h,name
 assert 'Invalid memory read' in (out/'pre-storage-fixture-span-fix/failure.log').read_text()
 print('Health-event consumers:6 bodies/236 native bytes;92320 checks including4032 callbacks;57 main imports;storage/notify and dispatcher gates remain')
if __name__=='__main__':audit()

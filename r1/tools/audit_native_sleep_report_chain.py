#!/usr/bin/env python3
"""Authenticate whole local sleep-chain composition without importing emulator."""
import hashlib,json
from build_native_dfu_backend_runtime import allocated_sections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-report-chain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 v=json.loads((OUT/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in v['inputs'].items():assert sha(ROOT/p)==h,p
 assert sha(ROOT/'r1/tools/verify_native_sleep_report_chain.py')==v['driver_sha256'] and v['workflows']==864 and v['record_comparisons']==4320 and v['counts']['workflows']==864 and v['counts']['records']==4320 and v['counts']=={'workflows':864,'records':4320,'reads':12044,'writes':4736,'erases':280,'crc':2144} and v['trace_sha256']=='8624e86034024896338ccaee12c80f03785e11753bd43a10353cb368d277e9ed'
 original=json.loads((BASE/'report.json').read_text());unit=next(u for u in original['units'] if u['source']=='r1/source/stock_checksums.c');assert unit['compiled'] and unit['source_sha256']==sha(ROOT/unit['source']) and unit['object_sha256']==sha(BASE/'r1__source__stock_checksums.c.o')
 spans=v['source_spans'];assert len(spans)==15
 assert sha(OUT/'source-chain-proof.elf')==v['proof_elf_sha256'] and sha(OUT/'source-chain-layout.ld')==v['proof_layout_sha256'];sections=allocated_sections(OUT/'source-chain-proof.elf')
 for x in spans:
  assert sections[x['section']][2]==x['size'] and sections[x['section']][4]==x['sha256']
  if x['native_exact']:
   a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
  elif x['section']=='.context':assert x['address']=='0x200067b4' and x['size']==12 and hashlib.sha256(bytes(12)).hexdigest()==x['sha256']
  else:assert x['section']=='.crc' and x['address']=='0x5d87c' and x['size']==516
 assert sum(x['size'] for x in spans if x['native_exact'] and x['section']!='.tables')==v['native_exact_storage_bytes']==3694 and v['native_exact_checksum_table_bytes']==1536 and v['source_crc_text_bytes']==516
 assert v['actual_record_event_select_fallback_write_finalize_erase_count_and_c_crc_execute'] and v['independent_repeated_append_error_and_flash_image_oracle'] and v['io_image_publish_memclear_mode_log_and_throttle_are_fixtures'] and v['actual_sleep_report_executes'] and v['crc_standalone_placement_overlaps_unused_native_crc_routines'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Sleep local chain:864 workflows/4320 report comparisons;3694 exact storage bytes;actual C CRC;68 main imports;I/O/runtime/layout/image gates open')
if __name__=='__main__':audit()

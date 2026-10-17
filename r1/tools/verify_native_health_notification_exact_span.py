#!/usr/bin/env python3
"""Check source-compiled throttle body/literal at native verification placement."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-health-notification-throttle';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 b=json.loads((OUT/'report.json').read_text());c=json.loads((OUT/'contracts.json').read_text());obj=OUT/'native_health_notification_throttle.o';assert sha(obj)==b['units'][0]['object_sha256'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 with tempfile.TemporaryDirectory(prefix='r1-notify-exact-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .body 0x8b138 : { *(.text.r1_health_event_notification_throttle) } .last 0x200067a4 : { *(.r1.health.notify.last) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'exact.elf';body=d/'body.bin';bindings={n:int(a,16)|1 for a,n in c['providers'].items()};cmd=['arm-none-eabi-ld','-T',str(ld),'-e','r1_health_event_notification_throttle',*[f'--defsym={n}={a}' for n,a in bindings.items()],str(obj),'-o',str(elf)];subprocess.run(cmd,check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.body','-O','binary',str(elf),str(body)],check=True);compiled=body.read_bytes();expected=raw[0x8b138-0x27000:0x8b184-0x27000]
  receipt=dict(report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),address='0x8b138',compiled_bytes=len(compiled),native_bytes=76,compiled_sha256=hashlib.sha256(compiled).hexdigest(),native_sha256=hashlib.sha256(expected).hexdigest(),byte_identical=compiled==expected,native_provider_addresses_are_verification_bindings=bindings,source_owned_cell_address='0x200067a4',source_owned_cell_bytes=4,whole_provider_graph_identity_proven=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'exact-span-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));assert receipt['byte_identical'] and len(compiled)==76
if __name__=='__main__':main()

from pathlib import Path
import json,hashlib,struct
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
index_at_verify_start=sha((R/'.git/index').read_bytes())
x=json.loads((D/'stock-receipts.json').read_text());raw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert sha(raw)==x['payload_sha256'];im=raw[32:]
for r in x['ranges']:
 a=int(r['payload_offset'],16);v=raw[a:a+r['size']]
 assert v.hex()==r['original_bytes_hex'] and sha(v)==r['sha256']
for a,v in x['literal_words'].items():assert struct.unpack_from('<I',im,int(a,16)-0x3300)[0]==int(v,16)
# Decode original Thumb BL, independent of linker candidate.
a=0xa9f6;h1,h2=struct.unpack_from('<HH',im,a-0x3300);s=(h1>>10)&1;i1=1^((h2>>13)&1)^s;i2=1^((h2>>11)&1)^s
delta=(s<<24)|(i1<<23)|(i2<<22)|((h1&0x3ff)<<12)|((h2&0x7ff)<<1)
if s:delta-=1<<25
assert a+4+delta==0xaa44
stock=im[0xa9e4-0x3300:0xaa2c-0x3300]
assert (D/'libc_nano.a.init.bin').read_bytes()==stock
assert (D/'source-init-with-fini.bin').read_bytes()==stock
assert (D/'libc.a.init.bin').read_bytes()!=stock
assert (D/'source-init.bin').read_bytes()!=stock
acq=json.loads((D/'acquisition.json').read_text());assert sha((D/'init.c').read_bytes())==acq['sha256']
# Existing policy exclusions are inherited; verification does not write prior packets.
ns={'__file__':str(R/'g2/analysis/audio-notification-block-insertion-2026-10-09/seal.py')}
exec(Path(ns['__file__']).read_text().split('baseline =',1)[0],ns)
count=0;bad=[]
for root in ['g2/analysis','g2/components']:
 for m in (R/root).rglob('DELIVERABLES.json'):
  if m.parent in ns['TARGETS'] or m.parent==D:continue
  data=json.loads(m.read_text());files=data.get('files',{}) if isinstance(data,dict) else {}
  if not isinstance(files,dict):continue
  for n,v in files.items():
   expected=v if isinstance(v,str) else v.get('sha256') if isinstance(v,dict) else None
   if not expected:continue
   p=R/n if n.startswith(('g2/','r1/','docs/','third-party/')) else m.parent/n;count+=1
   if not p.is_file() or sha(p.read_bytes())!=expected:bad.append(str(p))
audit=json.loads((R/'g2/analysis/audio-queue-cmsis-source-closure-2026-10-09/preservation-before.json').read_text())['audit']
ab=[n for n,v in audit.items() if sha((R/n).read_bytes())!=(v if isinstance(v,str) else v['sha256'])]
ck=json.loads((R/'g2/analysis/rescan-2026-10-09T032723Z/snapshot.json').read_text())['checkpoints'];ck={n:sha((R/v['path']).read_bytes())==v['sha256'] for n,v in ck.items()}
index=sha((R/'.git/index').read_bytes());earlier=json.loads((R/'g2/analysis/iom-queue-offset-stock-binding-20261009-implementation/stock-receipts.json').read_text())['index_before']
p={'prior_sealed_entries':count,'seal_mismatches':bad,'audit_inputs':len(audit),'audit_mismatches':ab,'checkpoints':ck,'index_sha256':index,'index_matches_prior_track_sample':index==earlier,'index_stable_during_verify':index==index_at_verify_start}
assert not bad and not ab and all(ck.values()) and index==index_at_verify_start
# This optional output writes only this owned directory.
if __name__=='__main__':
 print(json.dumps({'result':'two exact complete 72-byte matches; two controls differ','preservation':p},indent=2))

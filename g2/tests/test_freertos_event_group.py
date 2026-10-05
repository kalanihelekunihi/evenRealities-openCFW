"""Exact pinned text and integrated callable event-group contract checks."""
import csv,hashlib,json,pathlib,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
COMP=ROOT/'g2/components/foundation/freertos_event_group'
def function(text,name):
 prefix='EventBits_t ' if name=='xEventGroupSetBits' else 'void ' if name=='vEventGroupSetBitsCallback' else 'BaseType_t '
 start=text.index(prefix+name+'(');brace=text.index('{',start);depth=1;i=brace+1
 while depth:
  if text[i]=='{':depth+=1
  elif text[i]=='}':depth-=1
  i+=1
 return text[start:i]
class EventGroupEvidence(unittest.TestCase):
 def test_exact_pinned_source_text_and_license(self):
  p=json.loads((COMP/'SOURCE_PROVENANCE.json').read_text());self.assertEqual(p['upstream_commit'],'def7d2df2b0506d3d249334974f51e427c17a41c')
  for name,h in p['unchanged_function_text_sha256'].items():
   file=COMP/('timer_pend_subset.c' if name.startswith('xTimer') else 'event_groups_subset.c');raw=file.read_bytes();self.assertEqual(hashlib.sha256(function(raw.decode(),name).encode()).hexdigest(),h);self.assertIn(b'Copyright (C) 2021 Amazon.com',raw);self.assertIn(b'SPDX-License-Identifier: MIT',raw)
  for x in p['upstream_files']:
   path=ROOT/'g2/build/foundation/freertos-upstream'/x['path']
   if path.exists():
    raw=path.read_bytes();self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),x['git_blob'])
 def test_stock_function_identities(self):
  raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),'36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863')
  rows={int(x['address'],16):x for x in csv.DictReader((ROOT/'g2/symbols/apollo_main.tsv').read_text().splitlines(),delimiter='\t')}
  for pc in [0x47ed76,0x47ee4a,0x47eb4a]:
   x=rows[pc];off=pc-0x438000+32;self.assertEqual(hashlib.sha256(raw[off:off+int(x['size'])]).hexdigest(),x['stock_sha256'])
  off=0x47ee1e-0x438000+32;self.assertEqual(hashlib.sha256(raw[off:off+8]).hexdigest(),'3497dc0fa15f3c8bf59fea82f558007401ba0b03fc81a0fb1c3087ce1a9b6a73') # callback omitted from original symbol census
 def test_real_provider_functions_are_linked(self):
  elf=ROOT/'g2/build/foundation/event-group-wsf-simulator/event_group_wsf.elf'
  if not elf.exists():self.skipTest('event-group callable target not built')
  nm=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True)
  for n in ['xEventGroupSetBits','xEventGroupSetBitsFromISR','vEventGroupSetBitsCallback','xTimerPendFunctionCallFromISR','opencfw_wsf_notify_task','opencfw_wsf_notify_isr','opencfw_wsf_dispatch','GPIO0_607F_IRQHandler']:self.assertIn(' T '+n,nm)
  self.assertIn('event-group-wsf-simulator-test: event-group-wsf-simulator',(ROOT/'g2/Makefile').read_text())
 def test_optimized_verifier_is_rejected(self):
  p=subprocess.run(['python3','-O',str(COMP/'simulator/verify.py')],capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)

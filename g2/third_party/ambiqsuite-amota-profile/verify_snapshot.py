#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXPECTED={
 'amota_main.c':(21593,'63c89982b2c0392d9a603780ea3227ff1fb0a2f67680d81f05607b1475cc2d35','91a80afc7faea435e947a4e0c3841c41ba0ec481'),
 'amota_api.h':(4086,'b796bdfe494aefdc306161183103369d5d5b3be39edf9eb72753ca34868fa068','591f79aabf0a1b1b174bc544cc0774ae52c09d58'),
 'amotas_api.h':(4251,'6cfb5988cd49d6ea49bb157e7e742ef495796a50624713659830a8dd9eaf2050','e0647018f3121eee2432177f26a1971645826090'),
}
def sha(x):return hashlib.sha256(x).hexdigest()
def blob(x):return hashlib.sha1(f'blob {len(x)}\0'.encode()+x,usedforsecurity=False).hexdigest()
def verify():
 p=json.loads((HERE/'PROVENANCE.json').read_text());u=p['upstream'];records={x['path']:x for x in p['files']}
 assert u['selected_commit']=='de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f' and u['earliest_authenticated_stable_skeleton_commit']=='ca79fc6e140d25b0c596a5c87c3d311cd2710ad9'
 assert u['historical_g2_generating_commit'] is None and len(u['release_commits'])==4 and set(records)==set(EXPECTED)
 for n,v in EXPECTED.items():
  raw=(HERE/n).read_bytes();assert (len(raw),sha(raw),blob(raw))==v;assert (records[n]['size'],records[n]['sha256'],records[n]['git_blob_sha1'])==v
 src=(HERE/'amota_main.c').read_text()
 for token in ('AMOTA_RESET_TIMER_IND = AMOTA_MSG_START','AMOTA_DISCONNECT_TIMER_IND','static void amotaProcCccState','static void amotaProcMsg','void AmotaHandlerInit','void AmotaHandler'):
  assert token in src
 assert 'ccc state ind value:%d handle:%d idx:%d' in src and 'AMOTA_MSG_START               0xA0' in src
 return {'files':3,'selected_release':'2.5.1','selected_commit':u['selected_commit'],'stable_release_imports':4,'historical_g2_generating_commit':None}
if __name__=='__main__':print(json.dumps(verify(),indent=2,sort_keys=True));print('AmbiqSuite AMOTA-profile snapshot: PASS')

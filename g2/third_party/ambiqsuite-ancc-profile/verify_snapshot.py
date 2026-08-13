#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXPECTED={
 'ancc_main.c':(25099,'1435b838f7a7b18cec6f0b24f49266d4254c2d10f3ed6dd08eb029193069002d','4023359bf02612b07ed95f51561e7b8e7936810c'),
 'ancc_api.h':(11988,'c1af7746ddb649c2906b4ee69d06bf2d234baabad8197d3d7dba3754826cfce6','5594c66a09026d49592ae1a0983c75ffc0c1ec53'),
}
FUNCTIONS=('AnccSvcDiscover','AnccInit','AnccConnOpen','AnccConnClose','anccNoConnActive','anccActionListPush','anccActionListPop','AnccActionStart','AnccActionStop','AnccGetNotificationAttribute','AncsGetAppAttribute','AncsPerformNotiAction','AnccActionHandler','anccAttrHandler','AnccNtfValueUpdate','AnccCbackRegister','AnccStartServiceDiscovery')
def sha256(x):return hashlib.sha256(x).hexdigest()
def blob(x):return hashlib.sha1(f'blob {len(x)}\0'.encode()+x,usedforsecurity=False).hexdigest()
def verify():
 p=json.loads((HERE/'PROVENANCE.json').read_text());u=p['upstream']
 assert u['selected_commit']=='de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f'
 assert u['earliest_authenticated_same_implementation_commit']=='ca79fc6e140d25b0c596a5c87c3d311cd2710ad9'
 assert u['historical_g2_generating_commit'] is None and len(u['compatible_release_commits'])==4
 records={x['path']:x for x in p['files']};assert set(records)==set(EXPECTED)
 for name,(size,digest,oid) in EXPECTED.items():
  raw=(HERE/name).read_bytes();assert (len(raw),sha256(raw),blob(raw))==(size,digest,oid)
  assert (records[name]['size'],records[name]['sha256'],records[name]['git_blob_sha1'])==(size,digest,oid)
 src=(HERE/'ancc_main.c').read_text();assert sha256(''.join(src.splitlines(keepends=True)[48:]).encode())==u['implementation_body_sha256']
 for name in FUNCTIONS:assert src.count(name+'(')>=1
 assert '#define ANCC_LIST_ELEMENTS                  64' in (HERE/'ancc_api.h').read_text()
 assert 'ANCC_ATTRI_BUFFER_SIZE_BYTES        512' in (HERE/'ancc_api.h').read_text()
 return {'files':2,'upstream_source_definitions':len(FUNCTIONS),'selected_release':'2.5.1','selected_commit':u['selected_commit'],'historical_g2_generating_commit':None}
if __name__=='__main__':print(json.dumps(verify(),indent=2,sort_keys=True));print('AmbiqSuite ANCC-profile snapshot: PASS')

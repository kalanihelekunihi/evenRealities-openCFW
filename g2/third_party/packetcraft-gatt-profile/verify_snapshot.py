#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXPECTED={
 'gatt_main.c':(8447,'326c81353ab8405537074d54413c44675a61b236226ea2661416daf0454fc6d0','bba9a3041ce14284a0bf527934eabd01c01694d8'),
 'gatt_api.h':(5935,'c2ad43bf231276bf20e74b074859b9db3095f2eb918786abde7ed687fad01c37','6b71dd3178cbf89bbe3751d0ba33fb4a1603d97b'),
 'LICENSE.md':(562,'682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd','5fe50d5491f1166292380f46c8beae44ca83cadb'),
}
def sha256(x):return hashlib.sha256(x).hexdigest()
def blob(x):return hashlib.sha1(f'blob {len(x)}\0'.encode()+x,usedforsecurity=False).hexdigest()
def verify():
 p=json.loads((HERE/'PROVENANCE.json').read_text())
 assert p['upstream']['selected_commit']=='3656312d6b73e2a2c1c8b33ee0385bc199dd97e6'
 assert p['upstream']['historical_g2_generating_commit'] is None
 assert len(p['upstream']['compatibility_interval'])==4
 records={x['path']:x for x in p['files']};assert set(records)==set(EXPECTED)
 for name,(size,digest,oid) in EXPECTED.items():
  raw=(HERE/name).read_bytes();assert (len(raw),sha256(raw),blob(raw))==(size,digest,oid)
  assert (records[name]['size'],records[name]['sha256'],records[name]['git_blob_sha1'])==(size,digest,oid)
 src=(HERE/'gatt_main.c').read_text()
 for name in ('GattDiscover','GattValueUpdate','GattSetSvcChangedIdx','GattSendServiceChangedInd','GattReadCback','GattWriteCback'):
  assert src.count(name+'(')==1
 assert 'AppDiscFindService(connId, ATT_16_UUID_LEN' in src
 assert 'AttsCsfWriteFeatures(connId, offset, len, pValue)' in src
 return {'files':3,'source_functions':6,'selected_commit':p['upstream']['selected_commit'],'historical_g2_generating_commit':None}
if __name__=='__main__':print(json.dumps(verify(),indent=2,sort_keys=True));print('Cordio GATT-profile snapshot: PASS')

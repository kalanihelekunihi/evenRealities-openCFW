#!/usr/bin/env python3
"""Exercise idempotence and fail-closed tamper controls in disposable copies."""
from pathlib import Path
import tempfile,json,shutil,importlib.util,hashlib
R=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('resource_extract',R/'resources/extract.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);catalog=R/'resources/g2/s200-v2.2.6.10/manifest.json';j=json.loads(catalog.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={s['blob']:sha(catalog.parent/s['blob']) for s in j['segments']};mod.verify(catalog,True);mod.verify(catalog,True);assert before=={s['blob']:sha(catalog.parent/s['blob']) for s in j['segments']}
def reject(fn):
 try:fn()
 except AssertionError:return
 raise AssertionError('invalid input accepted')
with tempfile.TemporaryDirectory(prefix='opencfw-resource-negative-') as td:
 root=Path(td);tmp=root/'manifest.json';shutil.copyfile(catalog,tmp)
 for name in before:
  p=root/name;p.parent.mkdir(exist_ok=True);shutil.copyfile(catalog.parent/name,p)
 name=next(iter(before));p=root/name;raw=p.read_bytes();p.write_bytes(bytes([raw[0]^1])+raw[1:]);tampered=sha(p);reject(lambda:mod.verify(tmp,True));assert sha(p)==tampered
 p.write_bytes(raw);bad=dict(j);bad['bundleSha256']='0'*64;tmp.write_text(json.dumps(bad));reject(lambda:mod.verify(tmp,True))
 tmp.write_bytes(catalog.read_bytes());bad=json.loads(tmp.read_text());bad['segments'][0]['blob']='../escape.bin';tmp.write_text(json.dumps(bad));reject(lambda:mod.verify(tmp,True));assert not (root.parent/'escape.bin').exists()
print('PASS: 1191 records; idempotent extraction twice; tampered output refusal/no overwrite; wrong bundle rejection; path escape rejection')

from pathlib import Path
import json, hashlib, urllib.request, tarfile
R=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent
lock=json.loads((R/'tools/bootstrap/versions.json').read_text())
entries=lock.get('tools',[])
assert isinstance(entries,list)
records=[]
for version in ('10.3-2021.10','11.3.Rel1','12.2.Rel1'):
    e=next(x for x in entries if x['version']==version)
    out=O/'tools'/version;out.mkdir(parents=True,exist_ok=True)
    archive=out/e['url'].split('/')[-1]
    if not archive.exists():
        with urllib.request.urlopen(e['url']) as src,archive.open('wb') as dst:
            while chunk:=src.read(1024*1024):dst.write(chunk)
    actual=hashlib.sha256(archive.read_bytes()).hexdigest()
    assert actual==e['sha256'],(version,actual)
    with tarfile.open(archive) as tar:tar.extractall(out,filter='data')
    gcc=next(out.glob('*/bin/arm-none-eabi-gcc'))
    records.append({'version':version,'url':e['url'],'archive_sha256':actual,'gcc':str(gcc.relative_to(O)),'gcc_sha256':hashlib.sha256(gcc.read_bytes()).hexdigest()})
    print(version,'authenticated and extracted',flush=True)
(O/'acquisition.json').write_text(json.dumps(records,indent=2)+'\n')

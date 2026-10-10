#!/usr/bin/env python3
import hashlib,json,pathlib,xml.etree.ElementTree as ET,zipfile
ROOT=pathlib.Path(__file__).resolve().parent
out={}
for path in sorted((ROOT/'acquisitions').glob('*pdsc.xml')):
 tree=ET.parse(path).getroot()
 out[path.name]={
  'package':tree.findtext('vendor')+'.'+tree.findtext('name'),
  'repository':tree.findtext('repository'),
  'releases':[dict(item.attrib,notes=' '.join(''.join(item.itertext()).split())) for item in tree.findall('./releases/release')],
  'files':[item.attrib for item in tree.findall('.//file')],
  'components':[item.attrib for item in tree.findall('./components/component')],
 }
index=ET.parse(ROOT/'acquisitions/keil-pack-index.xml').getroot()
entries=index.findall('.//pdsc')
out['pack-index']={'count':len(entries),'em9305_entries':[e.attrib for e in entries if 'em9305' in str(e.attrib).lower()], 'relevant_entries':[e.attrib for e in entries if any(s in str(e.attrib).lower() for s in ['ambiq','stm32g0','cat2_dfp','arm_compiler'])]}
archive=ROOT/'acquisitions/apollo-1.5.2.pack'
if archive.exists():
 with zipfile.ZipFile(archive) as z:
  selected=[n for n in z.namelist() if ('apollo510' in n.lower() and n.lower().endswith(('.c','.s','.h','.sct','.scf'))) or n.lower().endswith(('.pdsc','license.txt'))]
  items=[]
  for name in selected:
   assert not pathlib.PurePosixPath(name).is_absolute() and '..' not in pathlib.PurePosixPath(name).parts
   body=z.read(name); target=ROOT/'apollo-selected'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
   items.append({'member':name,'size':len(body),'sha256':hashlib.sha256(body).hexdigest()})
  out['apollo-pack']={'total_members':len(z.namelist()),'crc_failure':z.testzip(),'selected':items}
(ROOT/'inventory.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:{'releases':len(v.get('releases',[])),'files':len(v.get('files',[])), 'members':v.get('total_members'), 'selected':len(v.get('selected',[])), 'entries':v.get('relevant_entries')} for k,v in out.items()},indent=2))

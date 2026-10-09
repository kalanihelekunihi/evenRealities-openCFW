from pathlib import Path
import json,hashlib,subprocess,urllib.request,io
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pin='7923059bff6c120c6fb74b63c7553ea345c0a8f3';srcdir=O/'source';srcdir.mkdir(exist_ok=True);source=srcdir/'memset.c';url='https://raw.githubusercontent.com/mirror/newlib-cygwin/'+pin+'/newlib/libc/string/memset.c'
if not source.exists():source.write_bytes(urllib.request.urlopen(url,timeout=30).read())
headers=R/'g2/analysis/touch-newlib14-memcpy-2026-10-09/source';troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';meta=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/meta['gcc']).parents[1];out=O/'outputs';out.mkdir(exist_ok=True)
common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{srcdir}:/source:ro','-v',f'{headers}:/headers:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'];flags=['-mcpu=cortex-m0plus','-mthumb','-Os','-ffunction-sections','-fdata-sections','-specs=nano.specs','-I/headers/newlib/libc/string'];argv=common+['/tool/bin/arm-none-eabi-gcc',*flags,'-c','/source/memset.c','-o','/out/public.o'];p=subprocess.run(argv,capture_output=True,text=True,check=True)
for option,suffix in [('-E','i'),('-M','d')]:subprocess.run(common+['/tool/bin/arm-none-eabi-gcc',*flags,option,'/source/memset.c','-o','/out/public.'+suffix],capture_output=True,text=True,check=True)
inputs={}
for path in (out/'public.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
 for prefix,host in [('/source/',srcdir),('/headers/',headers),('/tool/',tool)]:
  if path.startswith(prefix):inputs[path]=sha(host/path[len(prefix):]);break
 else:raise AssertionError(path)
with (out/'public.o').open('rb') as f:
 e=ELFFile(f);s=e.get_section_by_name('.text.memset');d=s.data();assert e.get_section_by_name('.rel.text.memset') is None
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';stock=fw.read_bytes()[32+0xa9d4-0x3300:32+0xa9e4-0x3300];archive=tool/'arm-none-eabi/lib/thumb/v6-m/nofp/libc_nano.a';blob=archive.read_bytes();off=8;strings=b'';member=None
while off<len(blob):
 h=blob[off:off+60];n=int(h[48:58]);name=h[:16].decode().strip();data=blob[off+60:off+60+n]
 if name=='//':strings=data
 elif name.startswith('/') and name[1:].isdigit():
  k=int(name[1:]);name=strings[k:strings.index(b'/\n',k)].decode()
 else:name=name.rstrip('/')
 if name=='libc_a-memset.o':member=data;break
 off+=60+n+(n%2)
assert member;ae=ELFFile(io.BytesIO(member));archtext=ae.get_section_by_name('.text.memset').data()
result={'source_revision':pin,'source_url':url,'source_sha256':sha(source),'compile_argv':argv,'diagnostics':p.stderr,'consumed_inputs':inputs,'preprocessed_sha256':sha(out/'public.i'),'object_sha256':sha(out/'public.o'),'text_bytes':len(d),'exact_stock':d==stock,'exact_nano_archive':d==archtext,'text_sha256':hashlib.sha256(d).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'archive_sha256':sha(archive),'archive_member_sha256':hashlib.sha256(member).hexdigest(),'runtime_extent':['0xA9D4','0xA9E4'],'license_file_reference':str((headers/'COPYING.NEWLIB').relative_to(R)),'license_sha256':sha(headers/'COPYING.NEWLIB'),'independent_review':'pending','denominator_54_increment':0,'limits':'Focused unmodified generic newlib size-branch source comparator with real vendor headers, not unique producing TU/build configuration or whole firmware source completion.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('memset source->stock',d==stock,'source->nano',d==archtext,'bytes',len(d))

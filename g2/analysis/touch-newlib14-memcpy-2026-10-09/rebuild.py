from pathlib import Path
import json,hashlib,subprocess,io
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=json.loads((O/'acquisition.json').read_text())
for x in a['files']:assert sha(O/x['local'])==x['sha256']
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';meta=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/meta['gcc']).parents[1];out=O/'outputs';out.mkdir(exist_ok=True);source=O/'source'
common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{source}:/source:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'];flags=['-mcpu=cortex-m0plus','-mthumb','-Os','-ffunction-sections','-fdata-sections','-specs=nano.specs','-I/source/include','-I/source/newlib/libc/string'];src='/source/newlib/libc/machine/arm/memcpy-stub.c';argv=common+['/tool/bin/arm-none-eabi-gcc',*flags,'-c',src,'-o','/out/public.o'];p=subprocess.run(argv,capture_output=True,text=True)
result={'source_revision':a['revision'],'argv':argv,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr,'independent_review':'pending','denominator_54_increment':0,'selection_basis':'Stock bytes match nano archive rather than regular archive; unchanged source stub selects generic size branch under __OPTIMIZE_SIZE__. Official Category2 recipe specifies nano.specs; focused compiler flags are not authenticated vendor full build flags.'}
if p.returncode==0:
 for option,suffix in [('-E','i'),('-M','d')]:subprocess.run(common+['/tool/bin/arm-none-eabi-gcc',*flags,option,src,'-o','/out/public.'+suffix],capture_output=True,text=True,check=True)
 deps=(out/'public.d').read_text().replace('\\\n',' ').split(':',1)[1].split();inputs={}
 for path in deps:
  if path.startswith('/source/'):host=source/path[len('/source/'):]
  elif path.startswith('/tool/'):host=tool/path[len('/tool/'):]
  else:raise AssertionError(path)
  inputs[path]=sha(host)
 with (out/'public.o').open('rb') as f:
  e=ELFFile(f);s=e.get_section_by_name('.text.memcpy');d=s.data();assert e.get_section_by_name('.rel.text.memcpy') is None
 fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';stock=fw.read_bytes()[32+0xaa2c-0x3300:32+0xaa3e-0x3300];archives=[]
 for lib in ['libc.a','libc_nano.a']:
  archive=tool/'arm-none-eabi/lib/thumb/v6-m/nofp'/lib;blob=archive.read_bytes();off=8;strings=b'';member=None
  while off<len(blob):
   h=blob[off:off+60];n=int(h[48:58]);name=h[:16].decode().strip();data=blob[off+60:off+60+n]
   if name=='//':strings=data
   elif name.startswith('/') and name[1:].isdigit():
    k=int(name[1:]);name=strings[k:strings.index(b'/\n',k)].decode()
   else:name=name.rstrip('/')
   if name=='libc_a-memcpy-stub.o':member=data;break
   off+=60+n+(n%2)
  assert member;ae=ELFFile(io.BytesIO(member));text=ae.get_section_by_name('.text.memcpy').data();archives.append({'library':lib,'archive_sha256':sha(archive),'member_sha256':hashlib.sha256(member).hexdigest(),'text_bytes':len(text),'matches_source_rebuild':text==d,'matches_stock_18_byte_extent':text==stock})
 result.update({'object_sha256':sha(out/'public.o'),'preprocessed_sha256':sha(out/'public.i'),'consumed_inputs':inputs,'compiled_bytes':len(d),'source_text_sha256':hashlib.sha256(d).hexdigest(),'stock_text_sha256':hashlib.sha256(stock).hexdigest(),'exact_stock':d==stock,'archives':archives,'runtime_extent':['0xAA2C','0xAA3E'],'source_rebuild':True,'limits':'Focused genuine source-provider comparison, not whole vendor build reproduction or firmware source completeness. No executable blobs/stubs used as source; unmodified acquired source and installed vendor nano headers/configuration hashed.'})
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('compile',p.returncode,'exact source->stock',result.get('exact_stock'));print(p.stderr)

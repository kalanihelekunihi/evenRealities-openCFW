from pathlib import Path
import json,hashlib,subprocess,io
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];m=json.loads((R/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text())[0];T=(R/'g2/analysis/touch-compiler14-successor-2026-10-09'/m['gcc']).parents[1];out=O/'halt-output-attempt2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{T}:/tool:ro','-v',f'{O}/configure-source:/source:ro','-v',f'{out}:/out','-w','/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55']
flags=['-mcpu=cortex-m0plus','-mthumb','-g','-O2','-ffunction-sections','-fdata-sections','-I/out'];calls=[]
for opt,suffix in [('-c','o'),('-E','i'),('-M','d')]:
 argv=common+['/tool/bin/arm-none-eabi-gcc',*flags,opt,'/source/libgloss/libnosys/_exit.c','-o','/out/default-halt.'+suffix];p=subprocess.run(argv,capture_output=True,text=True);calls.append({'argv':argv,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr});assert p.returncode==0,p.stderr
with (out/'default-halt.o').open('rb') as f:d=ELFFile(f).get_section_by_name('.text._exit').data()
archive=T/'arm-none-eabi/lib/thumb/v6-m/nofp/libnosys.a';blob=archive.read_bytes();off=8;strings=b'';member=None
while off<len(blob):
 h=blob[off:off+60];n=int(h[48:58]);name=h[:16].decode().strip();b=blob[off+60:off+60+n]
 if name=='//':strings=b
 elif name.startswith('/') and name[1:].isdigit():
  k=int(name[1:]);name=strings[k:strings.index(b'/\n',k)].decode()
 else:name=name.rstrip('/')
 if name=='_exit.o':member=b;break
 off+=60+n+n%2
assert member;ae=ELFFile(io.BytesIO(member));ad=ae.get_section_by_name('.text._exit').data();fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';stock=fw.read_bytes()[32+0xaa40-0x3300:32+0xaa44-0x3300]
inputs={}
for x in (out/'default-halt.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
 p=O/'configure-source'/x[len('/source/'):] if x.startswith('/source/') else out/x[len('/out/'):] if x.startswith('/out/') else T/x[len('/tool/'):];inputs[x]=sha(p)
result={'calls':calls,'bytes':len(d),'exact_archive':d==ad,'exact_stock':d==stock,'source_sha256':hashlib.sha256(d).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'archive_sha256':sha(archive),'member_sha256':hashlib.sha256(member).hexdigest(),'inputs':inputs,'flag_basis':'Pinned libgloss configure lines4080/4086 default GNU CFLAGS -g -O2 (or -O2). Function/data section layout is independently observed in authenticated archive. Prior size-optimized result has2bytes and remains retained; no source edits/flag sweep. This is a justified default comparator, not proof of original full vendor flags.','outputs':{str(p.relative_to(R)):sha(p) for p in out.glob('default-halt.*')},'independent_review':'pending','limits':'Source UB-prone arithmetic is removed under the tested compiler configuration. Stock/provider only branch forever; no physical divide-by-zero or successful operating-system exit claimed.'}
(O/'halt-default-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'bytes':len(d),'exact_archive':d==ad,'exact_stock':d==stock},indent=2))

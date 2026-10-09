"""One configuration-supported constructor and genuine GCC CRT comparison."""
from pathlib import Path
import json,hashlib,subprocess,io
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];P=R/'g2/analysis/touch-newlib14-startup-exit-2026-10-09';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text())[0];T=(R/'g2/analysis/touch-compiler14-successor-2026-10-09'/m['gcc']).parents[1]
out=O/'outputs';out.mkdir(parents=True,exist_ok=True)
common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{T}:/tool:ro','-v',f'{P}:/inputs:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55']
flags=['-mcpu=cortex-m0plus','-mthumb','-Os','-ffunction-sections','-fdata-sections','-specs=nano.specs']
calls=[];inputs={}
def command(args):
 p=subprocess.run(common+args,capture_output=True,text=True);calls.append({'argv':common+args,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr});(O/'commands.json').write_text(json.dumps(calls,indent=2)+'\n');assert p.returncode==0,p.stderr
def compile(label,src,extra):
 command(['/tool/bin/arm-none-eabi-gcc',*flags,*extra,'-c',src,'-o','/out/'+label+'.o'])
 for opt,suffix in [('-E','i'),('-M','d')]:command(['/tool/bin/arm-none-eabi-gcc',*flags,*extra,opt,src,'-o','/out/'+label+'.'+suffix])
 for x in (out/(label+'.d')).read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=P/x[len('/inputs/'):] if x.startswith('/inputs/') else T/x[len('/tool/'):];inputs[x]=sha(p)
compile('init','/inputs/source/newlib/libc/misc/init.c',['-D_HAVE_INIT_FINI'])
compile('crti','/inputs/gcc-source/libgcc/config/arm/crti.S',[])
compile('crtn','/inputs/gcc-source/libgcc/config/arm/crtn.S',[])
script=out/'bindings.ld';script.write_text('SECTIONS { .text 0xA9E4 : { *(.text.__libc_init_array) } .init 0xAA44 : { *(.init) } .fini 0xAA50 : { *(.fini) } /DISCARD/ : { *(.comment) *(.ARM.attributes) } }\n__preinit_array_start = 0x2000087C;\n__preinit_array_end = 0x2000087C;\n__init_array_start = 0x2000087C;\n__init_array_end = 0x20000880;\n')
command(['/tool/bin/arm-none-eabi-ld','-T','/out/bindings.ld','/out/init.o','/out/crti.o','/out/crtn.o','-o','/out/linked.elf'])
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 for name in ['.text','.init','.fini']:
  s=e.get_section_by_name(name);d=s.data();a=s['sh_addr'];stock=b[a-0x3300:a-0x3300+len(d)];rows.append({'section':name,'address':hex(a),'bytes':len(d),'mismatches':[i for i,(x,y) in enumerate(zip(d,stock)) if x!=y],'source_sha256':hashlib.sha256(d).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest()})
archive=T/'arm-none-eabi/lib/thumb/v6-m/nofp/libc_nano.a';blob=archive.read_bytes();off=8;strings=b'';checks=[]
while off<len(blob):
 h=blob[off:off+60];n=int(h[48:58]);name=h[:16].decode().strip();d=blob[off+60:off+60+n]
 if name=='//':strings=d
 elif name.startswith('/') and name[1:].isdigit():
  k=int(name[1:]);name=strings[k:strings.index(b'/\n',k)].decode()
 else:name=name.rstrip('/')
 if name=='libc_a-init.o':
  ae=ELFFile(io.BytesIO(d));asec=ae.get_section_by_name('.text.__libc_init_array')
  with (out/'init.o').open('rb') as f:se=ELFFile(f);sd=se.get_section_by_name('.text.__libc_init_array').data()
  checks.append({'member':name,'member_sha256':hashlib.sha256(d).hexdigest(),'raw_source_matches_archive':sd==asec.data(),'bytes':len(sd)})
 off+=60+n+n%2
for label in ['crti','crtn']:
 p=T/'lib/gcc/arm-none-eabi/14.2.1/thumb/v6-m/nofp'/(label+'.o')
 with p.open('rb') as f, (out/(label+'.o')).open('rb') as g:
  ae=ELFFile(f);se=ELFFile(g);checks.append({'provider':label,'installed_object_sha256':sha(p),'sections':{name:ae.get_section_by_name(name).data()==se.get_section_by_name(name).data() for name in ['.init','.fini']}})
result={'status':'PASS' if all(not x['mismatches'] for x in rows) else 'MISMATCH','source_configuration_basis':{'path':str((P/'source/newlib/configure.host').relative_to(R)),'sha256':sha(P/'source/newlib/configure.host'),'facts':'have_init_fini=yes line71; arm case does not override; lines952-953 append -D_HAVE_INIT_FINI. Macro is an actual library source-build setting, absent from installed client header.'},'inputs':inputs,'calls':calls,'stock_sections':rows,'provider_checks':checks,'archive_sha256':sha(archive),'historical_raw_mismatch_result_preserved':str((P/'results.json').relative_to(R)),'outputs':{str(p.relative_to(R)):sha(p) for p in sorted(out.iterdir()) if p.is_file()},'independent_review':'pending','limits':'Authentic source configuration and bounded provider/link comparison, not complete vendor configure/debug reproduction, live array content, reachability or whole-firmware source completion.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'stock_sections':rows,'provider_checks':checks},indent=2))

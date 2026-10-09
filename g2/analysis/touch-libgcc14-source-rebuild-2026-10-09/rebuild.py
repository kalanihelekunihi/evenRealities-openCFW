from pathlib import Path
import json,hashlib,subprocess,shutil
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();S=R/'g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/gcc-arm14-runtime';provenance=json.loads((S/'provenance.json').read_text())
for x in provenance['files']:assert sha(R/x['path'])==x['sha256']
assert provenance['revision_from_official_arm_release']=='a05ea1e5ee0867191bb432a84c055be99dbdbc16'
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1];out=O/'outputs';out.mkdir(exist_ok=True);runs=[]
common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{S}:/source:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'];source='/source/libgcc/config/arm/lib1funcs.S'
for member,selector in [('uidiv','L_udivsi3'),('zero','L_dvmd_tls')]:
 flags=['-mcpu=cortex-m0plus','-mthumb','-D'+selector];argv=common+['/tool/bin/arm-none-eabi-gcc',*flags,'-c',source,'-o','/out/'+member+'.o'];p=subprocess.run(argv,capture_output=True,text=True,check=True)
 for option,suffix in [('-E','s'),('-M','d')]:subprocess.run(common+['/tool/bin/arm-none-eabi-gcc',*flags,option,source,'-o','/out/'+member+'.'+suffix],capture_output=True,text=True,check=True)
 inputs={}
 for path in (out/(member+'.d')).read_text().replace('\\\n',' ').split(':',1)[1].split():
  assert path.startswith('/source/');inputs[path]=sha(S/path[len('/source/'):])
 with (out/(member+'.o')).open('rb') as f:
  e=ELFFile(f);s=e.get_section_by_name('.text');q=e.get_section_by_name('.rel.text');rel=[]
  if q:
   for r in q.iter_relocations():rel.append({'offset':r['r_offset'],'type':r['r_info_type'],'symbol':e.get_section(q['sh_link']).get_symbol(r['r_info_sym']).name})
  archive_member=R/'g2/analysis/touch-libgcc14-division-2026-10-09/outputs'/(member+'.o')
  with archive_member.open('rb') as a:ae=ELFFile(a);matches=s.data()==ae.get_section_by_name('.text').data()
  runs.append({'member':member,'selector':selector,'argv':argv,'diagnostics':p.stderr,'text_bytes':s['sh_size'],'raw_text_matches_authenticated_archive_member':matches,'relocations':rel,'consumed_inputs':inputs,'object_sha256':sha(out/(member+'.o')),'preprocessed_sha256':sha(out/(member+'.s')),'dependency_sha256':sha(out/(member+'.d')),'archive_member_sha256':sha(archive_member)})
shutil.copyfile(R/'g2/analysis/touch-libgcc14-division-2026-10-09/link.ld',out/'link.ld');argv=common+['/tool/bin/arm-none-eabi-ld','-T','/out/link.ld','/out/uidiv.o','/out/zero.o','-o','/out/linked.elf'];p=subprocess.run(argv,capture_output=True,text=True,check=True)
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 for name,a,n in [('division',0xa6c0,276),('zero',0xa9a8,4)]:
  d=e.get_section_by_name('.'+name).data();stock=b[a-0x3300:a-0x3300+n];rows.append({'section':name,'address':hex(a),'bytes':len(d),'exact_stock':d==stock,'sha256':hashlib.sha256(d).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest()})
result={'source_revision':provenance['revision_from_official_arm_release'],'source_provenance_sha256':sha(S/'provenance.json'),'compiler_sha256':sha(tool/'bin/arm-none-eabi-gcc'),'linker_sha256':sha(tool/'bin/arm-none-eabi-ld'),'provider_compilations':runs,'link_argv':argv,'link_diagnostics':p.stderr,'linked_elf_sha256':sha(out/'linked.elf'),'link_script_sha256':sha(out/'link.ld'),'sections':rows,'GPL3_sha256':sha(S/'COPYING3'),'runtime_exception_3_1_sha256':sha(S/'COPYING.RUNTIME'),'denominator_54_increment':0,'independent_review':'pending','limits':'Focused unchanged source-provider rebuild with source-declared selectors and target compiler macros. Vendor full configure/build recipe, object/debug equality, unique producer and firmware-wide source completeness remain unproven. No opcode arrays, retained executable blobs or replacement stubs used as source.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('raw provider matches',[(x['member'],x['raw_text_matches_authenticated_archive_member']) for x in runs]);print('stock linked matches',[(x['section'],x['exact_stock']) for x in rows])

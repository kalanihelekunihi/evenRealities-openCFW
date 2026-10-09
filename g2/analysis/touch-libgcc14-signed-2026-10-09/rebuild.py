from pathlib import Path
import hashlib,json,subprocess,shutil,io
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();S=R/'g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/gcc-arm14-runtime';prov=json.loads((S/'provenance.json').read_text())
for x in prov['files']:assert sha(R/x['path'])==x['sha256']
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';meta=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/meta['gcc']).parents[1];out=O/'outputs';out.mkdir(exist_ok=True)
common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{S}:/source:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'];flags=['-mcpu=cortex-m0plus','-mthumb','-DL_divsi3'];src='/source/libgcc/config/arm/lib1funcs.S';argv=common+['/tool/bin/arm-none-eabi-gcc',*flags,'-c',src,'-o','/out/signed.o'];p=subprocess.run(argv,capture_output=True,text=True,check=True)
for option,suffix in [('-E','s'),('-M','d')]:subprocess.run(common+['/tool/bin/arm-none-eabi-gcc',*flags,option,src,'-o','/out/public.'+suffix],capture_output=True,text=True,check=True)
inputs={path:sha(S/path[len('/source/'):]) for path in (out/'public.d').read_text().replace('\\\n',' ').split(':',1)[1].split()}
archive=tool/'lib/gcc/arm-none-eabi/14.2.1/thumb/v6-m/nofp/libgcc.a';blob=archive.read_bytes();off=8;member=None
while off<len(blob):
 h=blob[off:off+60];n=int(h[48:58]);name=h[:16].decode().strip()
 if name=='_divsi3.o/':member=blob[off+60:off+60+n];break
 off+=60+n+(n%2)
assert member
with (out/'signed.o').open('rb') as f:
 e=ELFFile(f);text=e.get_section_by_name('.text').data();ae=ELFFile(io.BytesIO(member));archive_match=text==ae.get_section_by_name('.text').data();assert len(text)==468
 q=e.get_section_by_name('.rel.text');relocs=[{'offset':v['r_offset'],'type':v['r_info_type'],'symbol':e.get_section(q['sh_link']).get_symbol(v['r_info_sym']).name} for v in q.iter_relocations()]
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];calls=[];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB);md.detail=True
for v in relocs:
 a=0xa7d4+v['offset'];i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert v['type']==10 and v['symbol']=='__aeabi_idiv0' and i.mnemonic=='bl' and i.operands[0].imm==0xa9a8;calls.append({'instruction':hex(a),'target':'0xA9A8'})
shutil.copyfile(R/'g2/analysis/touch-libgcc14-source-rebuild-2026-10-09/outputs/zero.o',out/'zero.o');(out/'link.ld').write_text('ENTRY(__aeabi_idiv)\nSECTIONS { .signed 0xA7D4 : { *signed.o(.text) } .zero 0xA9A8 : { *zero.o(.text) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');link=common+['/tool/bin/arm-none-eabi-ld','-T','/out/link.ld','/out/signed.o','/out/zero.o','-o','/out/linked.elf'];lp=subprocess.run(link,capture_output=True,text=True,check=True)
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f);d=e.get_section_by_name('.signed').data();stock=b[0xa7d4-0x3300:0xa9a8-0x3300];exact=d==stock
result={'source_revision':prov['revision_from_official_arm_release'],'compile_argv':argv,'diagnostics':p.stderr,'link_argv':link,'link_diagnostics':lp.stderr,'consumed_inputs':inputs,'source_object_sha256':sha(out/'signed.o'),'archive_sha256':sha(archive),'archive_member_sha256':hashlib.sha256(member).hexdigest(),'raw_source_matches_archive':archive_match,'exact_linked_stock':exact,'new_bytes':468,'reused_zero_hook_bytes':4,'text_sha256':hashlib.sha256(d).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'linked_elf_sha256':sha(out/'linked.elf'),'original_calls':calls,'relocations':relocs,'correct_extents':{'idiv':['0xA7D4','0xA9A0'],'idivmod':['0xA9A0','0xA9A8']},'historical_idivmod_row_overlaps_zero_hook':True,'denominator_54_increment':0,'independent_review':'pending','limits':'Focused unchanged source rebuild, not vendor full-build/object reproduction or whole firmware completeness. Original symbol rows preserved.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('signed source/archive',archive_match,'source/stock',exact,'bytes',len(d))

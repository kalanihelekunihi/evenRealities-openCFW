import pathlib,json,struct,tarfile
OUT=pathlib.Path(__file__).resolve().parent
SRC=pathlib.Path('g2/analysis/nationalchip-dsp-c-compiler-successor-20261009T195245Z')
ns={'__file__':str(OUT/'verify_dsp.py')}
exec((OUT/'verify_dsp.py').read_text().split('\nr=json.loads')[0],ns)
sha=ns['sha'];sections=ns['sections'];checks=[]
t=json.loads((SRC/'toolchain.json').read_text());r=json.loads((SRC/'c-build-complete-header-results.json').read_text());summary=json.loads((SRC/'comparison-summary.json').read_text());root=pathlib.Path(t['extracted_root'])
checks.append({'label':'archive SHA256','pass':sha(pathlib.Path(t['archive']).read_bytes())==t['archive_sha256']})
checks.append({'label':'extracted compiler SHA256','pass':sha((root/'bin/csky-abiv2-elf-gcc').read_bytes())==t['gcc_sha256']})
wanted=['bin/csky-elfabiv2-gcc','bin/csky-elfabiv2-as','libexec/gcc/csky-elfabiv2/6.3.0/cc1'];verified=set()
with tarfile.open(t['archive'],'r:gz') as tar:
 for m in tar:
  rel=next((x for x in wanted if m.name.endswith('/'+x)),None)
  if rel and m.isfile():
   b=tar.extractfile(m).read();checks.append({'label':'archive-extraction '+rel,'pass':b==(root/rel).read_bytes(),'archive_member':m.name,'sha256':sha(b)});verified.add(rel)
checks.append({'label':'all three compiler tool members found','pass':len(verified)==3})
headers=json.loads((SRC/'sdk-header-hashes.json').read_text());bad=[f for f,h in headers.items() if sha(pathlib.Path(f).read_bytes())!=h]
checks.append({'label':'retained SDK header snapshot','pass':not bad,'files':len(headers),'mismatches':bad})
expected_flags=['-mcpu=ck804ef','-mhard-float','-O2','-g','-fno-builtin','-fstrict-volatile-bitfields','-ffunction-sections','-fdata-sections']
expected_includes=['-I/repo/third-party/upstream/nationalchip-lvp-kws/'+x for x in ['include/utility/libdsp','include','arch/soc/grus/include','include/utility']]
original=json.loads((OUT/'DSP-INDEPENDENT-VERIFICATION.json').read_text());stock=pathlib.Path('g2/blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes();objects=[];undef=set();diff=[]
for row in r['results']:
 cmd=row['command'];src=pathlib.Path(row['source']);obj=SRC/pathlib.Path(cmd[-1]).name;b=obj.read_bytes();s=sections(b)
 ok=sha(src.read_bytes())==row['source_sha256'] and sha(b)==row['object_sha256'] and row['returncode']==0
 checks.append({'label':'source/object '+src.name,'pass':ok,'source_sha256':sha(src.read_bytes()),'object_sha256':sha(b)})
 i=cmd.index('/tool/bin/csky-abiv2-elf-gcc');actual=cmd[i+1:]
 ok=actual==expected_flags+expected_includes+['-c','/repo/'+row['source'],'-o','/out/'+obj.name] and '--network=none' in cmd and '--read-only' in cmd and 'linux/amd64' in cmd and 'opencfw/iar-base:10.10.2-local' in cmd
 mounts=[cmd[k+1] for k,x in enumerate(cmd) if x=='--mount'];ok=ok and len(mounts)==3 and mounts[0].endswith(',dst=/tool,readonly') and mounts[1].endswith(',dst=/repo,readonly') and mounts[2].endswith(',dst=/out')
 checks.append({'label':'fixed command/mount recipe '+src.name,'pass':ok})
 texts=[{'section':n,'bytes':h[5]} for n,h in s if n.startswith('.text.') and h[5]];local_undef=[]
 for n,h in s:
  if h[1]!=2:continue
  strings=s[h[6]][1];strings=b[strings[4]:strings[4]+strings[5]]
  for pos in range(h[4],h[4]+h[5],h[9]):
   name,value,size,info,other,shndx=struct.unpack_from('<IIIBBH',b,pos)
   if name and shndx==0:
    name=strings[name:].split(b'\0',1)[0].decode();local_undef.append(name);undef.add(name)
 checks.append({'label':'text-section summary '+obj.name,'pass':texts==summary['compiled_text_sections'][obj.name]})
 objects.append({'object':obj.name,'text_sections':texts,'undefined_symbols':local_undef})
 for c in row['comparisons']:
  h=next(h for n,h in s if n==c['section']);v=b[h[4]:h[4]+h[5]];m=next(x for x in original['matches'] if x['section']==c['section']);ref=stock[int(m['offsets'][0],16):int(m['offsets'][0],16)+m['bytes']]
  ok=len(v)==c['compiled_bytes'] and sha(v)==c['compiled_sha256'] and sha(ref)==c['assembly_reference']['expected_sha256'] and v!=ref and c['full_equal'] is False
  checks.append({'label':'whole-section mismatch '+c['section'],'pass':ok});diff.append({'section':c['section'],'compiled_bytes':len(v),'stock_bytes':len(ref),'full_equal':False})
checks.append({'label':'summary counts/undefined kernels','pass':summary['compiled_files']==5 and summary['failed_files']==0 and summary['exact_selected_sections']==0 and diff==summary['different_selected_sections'] and set(summary['unprovided_kernel_symbols'])==undef})
res={'all_pass':all(x['pass'] for x in checks),'checks':checks,'objects':objects,'different_sections':diff,'compile_rerun':False,'limits':'Retained commands and outputs independently verified. Successful C compilation does not establish numerical equivalence, stock producer recipe, final linking or byte identity. Archive verifies selected GCC/as/cc1 extraction; no live Docker image inspection repeated.'}
(OUT/'DSP-C-COMPILER-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({'all_pass':res['all_pass'],'checks':len(checks),'headers':len(headers),'failed':[x['label'] for x in checks if not x['pass']],'objects':objects},indent=2))

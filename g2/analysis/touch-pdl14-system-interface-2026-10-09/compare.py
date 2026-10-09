from pathlib import Path
import json,hashlib,subprocess
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sel=json.loads((O/'selection.json').read_text());targets=[x for x in sel['functions'] if x['status']=='predeclared_unchanged_source_comparison']
prior=R/'g2/analysis/touch-compiler14-successor-2026-10-09';e=json.loads((prior/'acquisition.json').read_text())[0];tool=(prior/e['gcc']).parents[1];P=prior/'tools/pdl-input';B=R/'g2/analysis/dependency-followup-2026-10-08/touch-source';fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()[32:]
flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-DCY8C4046FNI_T412','-ffunction-sections'];inc=['-I/interface','-I/headers','-I/headers/cmsis','-I/pdl/drivers/include','-I/pdl/devices/include','-I/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include'];results=[]
for unit in sorted({x['source_unit'] for x in targets}):
 out=O/'outputs'/unit;out.mkdir(parents=True,exist_ok=True);source=P/'drivers/source'/unit
 common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{P}:/pdl:ro','-v',f'{B}:/headers:ro','-v',f'{O / 'interface'}:/interface:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55']
 args=common+['/tool/bin/arm-none-eabi-gcc',*flags,*inc,'-c','/pdl/drivers/source/'+unit,'-o','/out/public.o'];run=subprocess.run(args,capture_output=True,text=True)
 rec={'source_unit':unit,'source_sha256':sha(source),'argv':args,'exit_code':run.returncode,'diagnostics':run.stdout+run.stderr,'functions':[]}
 if run.returncode==0:
  for option,suffix in [('-E','i'),('-M','d')]:
   cmd=common+['/tool/bin/arm-none-eabi-gcc',*flags,*inc,option,'/pdl/drivers/source/'+unit,'-o','/out/public.'+suffix];p=subprocess.run(cmd,capture_output=True,text=True,check=True)
  deps=(out/'public.d').read_text().replace('\\\n',' ').split(':',1)[1].split();hashes={}
  for name in deps:
   path=Path(name)
   for prefix,host in [('/pdl/',P),('/headers/',B),('/tool/',tool),('/interface/',O/'interface')]:
    if name.startswith(prefix):path=host/name[len(prefix):];break
   hashes[name]=sha(path)
  rec['consumed_input_hashes']=hashes;rec['output_hashes']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
  with (out/'public.o').open('rb') as f:
   elf=ELFFile(f)
   for t in (x for x in targets if x['source_unit']==unit):
    s=elf.get_section_by_name('.text.'+t['function']);row=dict(t)
    if s is None:row['comparison_status']='expected_section_absent'
    else:
     data=s.data();n=t['historical_code_bytes'];a=t['address'];stock=fw[a-0x3300:a-0x3300+n];rel=[]
     for q in elf.iter_sections():
      if q.name in ('.rel'+s.name,'.rela'+s.name):
       sy=elf.get_section(q['sh_link']);rel=[{'offset':v['r_offset'],'type':v['r_info_type'],'symbol':sy.get_symbol(v['r_info_sym']).name} for v in q.iter_relocations()]
     row.update({'compiled_bytes':len(data),'compiled_sha256':hashlib.sha256(data).hexdigest(),'relocations':rel,'overlap_mismatched_positions':[i for i in range(min(n,len(data))) if data[i]!=stock[i]],'comparison_status':'exact_complete_section' if data==stock and not rel else 'relocation_or_extent_boundary' if rel or len(data)!=n else 'same_extent_byte_mismatch'})
    rec['functions'].append(row)
 else:rec['functions']=[{**t,'comparison_status':'translation_unit_compile_failed'} for t in targets if t['source_unit']==unit]
 results.append(rec);(O/'results.json').write_text(json.dumps({'selection_sha256':sha(O/'selection.json'),'compiler':e,'units':results,'admitted':False},indent=2)+'\n');print(unit,run.returncode,[(x['function'],x['comparison_status']) for x in rec['functions']],flush=True)

from pathlib import Path
import json,hashlib,subprocess,urllib.request,io
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pin='7923059bff6c120c6fb74b63c7553ea345c0a8f3';S=O/'source';records=[]
for name in ['newlib/libc/misc/init.c','newlib/libc/stdlib/exit.c','newlib/libc/stdlib/atexit.h']:
 p=S/name;p.parent.mkdir(parents=True,exist_ok=True);url='https://raw.githubusercontent.com/mirror/newlib-cygwin/'+pin+'/'+name
 if not p.exists():p.write_bytes(urllib.request.urlopen(url,timeout=30).read())
 records.append({'upstream_path':name,'url':url,'sha256':sha(p)})
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';meta=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/meta['gcc']).parents[1];flags=['-mcpu=cortex-m0plus','-mthumb','-Os','-ffunction-sections','-fdata-sections','-specs=nano.specs'];fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];runs=[]
for label,name,function,address in [('init','newlib/libc/misc/init.c','__libc_init_array',0xa9e4),('exit','newlib/libc/stdlib/exit.c','exit',0xa9ac)]:
 out=O/'outputs'/label;out.mkdir(parents=True,exist_ok=True);common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{S}:/source:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'];argv=common+['/tool/bin/arm-none-eabi-gcc',*flags,'-c','/source/'+name,'-o','/out/public.o'];p=subprocess.run(argv,capture_output=True,text=True);rec={'function':function,'address':hex(address),'argv':argv,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr}
 if p.returncode==0:
  for option,suffix in [('-E','i'),('-M','d')]:subprocess.run(common+['/tool/bin/arm-none-eabi-gcc',*flags,option,'/source/'+name,'-o','/out/public.'+suffix],capture_output=True,text=True,check=True)
  inputs={}
  for path in (out/'public.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
   host=S/path[len('/source/'):] if path.startswith('/source/') else tool/path[len('/tool/'):];inputs[path]=sha(host)
  with (out/'public.o').open('rb') as f:
   e=ELFFile(f);s=e.get_section_by_name('.text.'+function);rec['function_emitted']=s is not None
   if s:
    d=s.data();mask=set();q=e.get_section_by_name('.rel'+s.name);rels=[]
    if q:
     for v in q.iter_relocations():mask.update(range(v['r_offset'],v['r_offset']+4));rels.append({'offset':v['r_offset'],'type':v['r_info_type'],'symbol':e.get_section(q['sh_link']).get_symbol(v['r_info_sym']).name})
    stock=b[address-0x3300:address-0x3300+len(d)];rec.update({'compiled_bytes':len(d),'relocations':rels,'non_relocated_mismatches':[i for i in range(len(d)) if i not in mask and d[i]!=stock[i]],'section_sha256':hashlib.sha256(d).hexdigest(),'stock_window_sha256':hashlib.sha256(stock).hexdigest(),'extent_not_promoted':True})
  rec.update({'object_sha256':sha(out/'public.o'),'preprocessed_sha256':sha(out/'public.i'),'consumed_inputs':inputs})
 runs.append(rec);(O/'results.json').write_text(json.dumps({'source_revision':pin,'source_acquisitions':records,'runs':runs,'independent_review':'pending','limits':'Fixed compiler/nano-header source comparison, not authenticated vendor full configuration or firmware extent/composition proof. All failures/mismatches retained.'},indent=2)+'\n');print(label,p.returncode,rec.get('compiled_bytes'),rec.get('non_relocated_mismatches'),flush=True)

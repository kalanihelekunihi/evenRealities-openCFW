from pathlib import Path
import json,hashlib,subprocess,shutil
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();D=R/'g2/analysis/source-discovery-parallel-2026-10-09/pdl-residual-history';pin='16aaf1d3d764ca3c426234c90cdeb6f19cb2d091'
provenance=json.loads((D/'provenance.json').read_text())+json.loads((D/'header-recipe-provenance.json').read_text())
for x in provenance:
 p=R/x.get('path',x.get('local'));assert sha(p)==x['sha256']
overlay=O/'historical-interface';overlay.mkdir(exist_ok=True)
for name in ['cy_flash.h','cy_device.h']:shutil.copyfile(D/(pin+'-'+name),overlay/name)
shutil.copyfile(D/(pin+'-cy_flash.c'),overlay/'cy_flash.c')
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1];P=troot/'tools/pdl-input';B=R/'g2/analysis/dependency-followup-2026-10-08/touch-source';I=R/'g2/analysis/touch-pdl14-system-interface-2026-10-09/interface'
flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-DCY8C4046FNI_T412','-ffunction-sections'];inc=['-I/interface','-I/headers','-I/headers/cmsis','-I/pdl/drivers/include','-I/pdl/devices/include','-I/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include'];targets={'cy_flash.c':[('Cy_Flash_ClockBackup',0x8cc4),('Cy_Flash_ClockConfig',0x8d00),('Cy_Flash_ClockRestore',0x8d20),('Cy_Flash_WriteRow',0x8d50)],'cy_sysclk.c':[('Cy_SysClk_IloStartMeasurement',0x9d90),('Cy_SysClk_IloStopMeasurement',0x9ddc),('Cy_SysClk_IloCompensate',0x9e18)],'cy_syspm.c':[('Cy_SysPm_ExecuteCallback',0xa444)]}
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];records=[]
for label,unit,old,data_sections in [('flash216-baseline','cy_flash.c',True,False),('flash216-data','cy_flash.c',True,True),('ilo-data','cy_sysclk.c',False,True),('pm-data','cy_syspm.c',False,True)]:
 out=O/'outputs'/label;out.mkdir(parents=True,exist_ok=True);extra=['-fdata-sections'] if data_sections else [];includes=(['-I/historical'] if old else [])+inc;src='/historical/cy_flash.c' if old else '/pdl/drivers/source/'+unit
 common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{P}:/pdl:ro','-v',f'{B}:/headers:ro','-v',f'{I}:/interface:ro','-v',f'{overlay}:/historical:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'];argv=common+['/tool/bin/arm-none-eabi-gcc',*flags,*extra,*includes,'-c',src,'-o','/out/public.o'];p=subprocess.run(argv,capture_output=True,text=True);rec={'label':label,'source_unit':unit,'historical_pin':pin if old else None,'source_sha256':sha(overlay/'cy_flash.c' if old else P/'drivers/source'/unit),'argv':argv,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr,'functions':[]}
 if p.returncode==0:
  for option,suffix in [('-E','i'),('-M','d')]:subprocess.run(common+['/tool/bin/arm-none-eabi-gcc',*flags,*extra,*includes,option,src,'-o','/out/public.'+suffix],capture_output=True,text=True,check=True)
  deps=(out/'public.d').read_text().replace('\\\n',' ').split(':',1)[1].split();inputs={}
  for name in deps:
   path=Path(name)
   for prefix,host in [('/pdl/',P),('/headers/',B),('/tool/',tool),('/interface/',I),('/historical/',overlay)]:
    if name.startswith(prefix):path=host/name[len(prefix):];break
   inputs[name]=sha(path)
  rec['consumed_input_hashes']=inputs;rec['output_hashes']={x.name:sha(x) for x in out.iterdir() if x.is_file()}
  with (out/'public.o').open('rb') as f:
   e=ELFFile(f)
   for name,a in targets[unit]:
    s=e.get_section_by_name('.text.'+name);d=s.data();q=e.get_section_by_name('.rel'+s.name);mask=set();rel=[]
    if q:
     for v in q.iter_relocations():
      sym=e.get_section(q['sh_link']).get_symbol(v['r_info_sym']);mask.update(range(v['r_offset'],v['r_offset']+4));rel.append({'offset':v['r_offset'],'type':v['r_info_type'],'symbol':sym.name,'symbol_section':e.get_section(sym['st_shndx']).name if isinstance(sym['st_shndx'],int) else sym['st_shndx']})
    stock=b[a-0x3300:a-0x3300+len(d)];diff=[i for i in range(len(d)) if i not in mask and d[i]!=stock[i]];rec['functions'].append({'function':name,'address':hex(a),'compiled_bytes':len(d),'relocations':rel,'non_relocated_mismatches':diff,'section_sha256':hashlib.sha256(d).hexdigest(),'stock_window_sha256':hashlib.sha256(stock).hexdigest(),'extent_not_yet_promoted':True})
 records.append(rec);(O/'results.json').write_text(json.dumps({'selection_sha256':sha(O/'SELECTION.md'),'discovery_provenance_sha256':sha(D/'provenance.json'),'recipe_provenance_sha256':sha(D/'header-recipe-provenance.json'),'runs':records,'independent_review':'pending','stock_flags_claim':False},indent=2)+'\n');print(label,p.returncode,[(x['function'],x['compiled_bytes'],len(x['non_relocated_mismatches'])) for x in rec['functions']],flush=True)

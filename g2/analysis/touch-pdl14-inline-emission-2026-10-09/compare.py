from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1];P=troot/'tools/pdl-input';B=R/'g2/analysis/dependency-followup-2026-10-08/touch-source';I=R/'g2/analysis/touch-pdl14-system-interface-2026-10-09/interface'
flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-DCY8C4046FNI_T412','-ffunction-sections','-fkeep-static-functions'];inc=['-I/interface','-I/headers','-I/headers/cmsis','-I/pdl/drivers/include','-I/pdl/devices/include','-I/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include']
common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{P}:/pdl:ro','-v',f'{B}:/headers:ro','-v',f'{I}:/interface:ro','-v',f'{O}:/task:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55']
argv=common+['/tool/bin/arm-none-eabi-gcc',*flags,*inc,'-c','/task/include.c','-o','/out/public.o'];p=subprocess.run(argv,capture_output=True,text=True,check=True)
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=fw.read_bytes()[32:];assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';rows=[]
with (out/'public.o').open('rb') as f:
 e=ELFFile(f)
 for name,a,n in [('Cy_SysClk_ClkHfGetDivider',0x9f34,10),('Cy_SysClk_ClkHfSetDivider',0x9f44,74),('Cy_SCB_SetRxFifoLevel',0x9316,44)]:
  s=e.get_section_by_name('.text.'+name);assert s is not None;data=s.data();rel=[]
  for q in e.iter_sections():
   if q['sh_type']=='SHT_REL' and q.name=='.rel'+s.name:
    for v in q.iter_relocations():rel.append({'offset':v['r_offset'],'type':v['r_info_type'],'symbol':e.get_section(q['sh_link']).get_symbol(v['r_info_sym']).name})
  stock=b[a-0x3300:a-0x3300+len(data)];rows.append({'function':name,'runtime_address':hex(a),'historical_code_bytes':n,'emitted_section_bytes':len(data),'exact_full_section':data==stock,'relocations':rel,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'mismatch_positions':[i for i in range(len(data)) if data[i]!=stock[i]]})
result={'argv':argv,'diagnostics':p.stderr,'emission_contract':'Include unchanged public headers and take addresses in three typed data pointers; authentic always-inline bodies emitted without implementation wrappers or -fno-inline. Keep-static alone did not emit them. Not a producing-TU/flag identity claim.','include_source_sha256':sha(O/'include.c'),'header_sha256':{n:sha(P/'drivers/include'/n) for n in ['cy_sysclk.h','cy_scb_common.h']},'object_sha256':sha(out/'public.o'),'functions':rows,'independent_review':'pending','limits':'Linkage/literal review needed for any residual. No source fitting or fabricated implementations.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['function'],x['exact_full_section'],x['emitted_section_bytes'],len(x['mismatch_positions'])) for x in rows])

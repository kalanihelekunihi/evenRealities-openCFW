from pathlib import Path
import json,hashlib,subprocess
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((R/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text())[0];T=(R/'g2/analysis/touch-compiler14-successor-2026-10-09'/m['gcc']).parents[1];plugin='/tool/lib/gcc/arm-none-eabi/14.2.1/plugin/include';prev=R/'g2/analysis/touch-crt-array-binding-2026-10-09';out=O/'outputs';out.mkdir(exist_ok=True)
common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{T}:/tool:ro','-v',f'{O}/source:/source:ro','-v',f'{O}:/task:ro','-v',f'{prev}:/previous:ro','-v',f'{out}:/out','-w','/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'];calls=[]
def command(args,output=None):
 p=subprocess.run(common+args,capture_output=True,text=True);calls.append({'argv':common+args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});(O/'commands.json').write_text(json.dumps(calls,indent=2)+'\n')
 if output and not p.returncode:(out/output).write_text(p.stdout)
 return p
p=command(['/bin/sh','/task/select-target.sh'],'target-selection.txt');assert p.returncode==0
sel=dict(x.split('=',1) for x in p.stdout.splitlines());assert sel['tm_file'].split()==['arm/bpabi-lib.h'];assert not sel['tm_define'] and not sel['tm_defines']
p=command(['/usr/bin/env','DEFINES=USED_FOR_TARGET','HEADERS=auto-host.h ansidecl.h','TARGET_CPU_DEFAULT=','/bin/sh','/source/gcc/mkconfig.sh','tconfig.h']);assert p.returncode==0
p=command(['/usr/bin/env','DEFINES='+sel['tm_defines'],'HEADERS='+sel['tm_file'],'/bin/sh','/source/libgcc/mkheader.sh'],'libgcc_tm.h');assert p.returncode==0
flags=['-mcpu=cortex-m0plus','-mthumb','-O2','-g0','-DIN_GCC','-finhibit-size-directive','-fno-inline','-fno-exceptions','-fno-zero-initialized-in-bss','-fno-toplevel-reorder','-fno-tree-vectorize','-fbuilding-libgcc','-fno-stack-protector','-ffunction-sections','-fdata-sections','-I/out','-I'+plugin,'-I/source/libgcc','-I/source/libgcc/config','-DCRT_BEGIN'];src='/previous/source/libgcc/crtstuff.c'
p=command(['/tool/bin/arm-none-eabi-gcc',*flags,'-c',src,'-o','/out/crtbegin.o']);result={'source_revision':'a05ea1e5ee0867191bb432a84c055be99dbdbc16','compile_exit':p.returncode,'source_rebuilt':False,'target_selection':sel,'generated_headers':{x:sha(out/x) for x in ['tconfig.h','libgcc_tm.h']},'flags_basis':'Exact pinned libgcc Makefile CRTSTUFF_CFLAGS + GCC internal IN_GCC + selected v6-M multilib. Function/data sections independently authenticated in archive. Installed authentic plugin target/config headers used, not invented headers. Full vendor configuration not claimed.'}
if not p.returncode:
 inputs={}
 for opt,suffix in [('-E','i'),('-M','d')]:
  q=command(['/tool/bin/arm-none-eabi-gcc',*flags,opt,src,'-o','/out/crtbegin.'+suffix]);assert q.returncode==0
 for x in (out/'crtbegin.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
  host=out/x[len('/out/'):] if x.startswith('/out/') else T/x[len('/tool/'):] if x.startswith('/tool/') else O/'source'/x[len('/source/'):] if x.startswith('/source/') else prev/x[len('/previous/'):];inputs[x]=sha(host)
 installed=T/'lib/gcc/arm-none-eabi/14.2.1/thumb/v6-m/nofp/crtbegin.o';rows=[]
 with installed.open('rb') as f,(out/'crtbegin.o').open('rb') as g:
  a=ELFFile(f);e=ELFFile(g)
  for s in a.iter_sections():
   if s.name.startswith('.text.') or s.name in ['.init_array','.fini_array']:
    t=e.get_section_by_name(s.name);rows.append({'section':s.name,'archive_bytes':s['sh_size'],'source_bytes':t['sh_size'] if t else None,'raw_equal':bool(t and t.data()==s.data())})
 result.update(source_rebuilt=True,consumed_inputs=inputs,sections=rows,all_selected_raw_equal=all(x['raw_equal'] for x in rows),installed_provider_sha256=sha(installed))
result['outputs']={str(p.relative_to(R)):sha(p) for p in out.iterdir() if p.is_file()};result['limits']='Focused genuine source comparator and generated-header provenance. Binary-provider attribution remains separate until source/link checks and independent review pass. No full vendor configure/build/debug identity or physical/live runtime claim.'
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'compile_exit':result['compile_exit'],'all_selected_raw_equal':result.get('all_selected_raw_equal'),'sections':result.get('sections')},indent=2))

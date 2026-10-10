from pathlib import Path
import json,subprocess,hashlib
from elftools.elf.elffile import ELFFile
r=Path('/Users/kalani/Repo/evenRealities-openCFW');d=Path(Path('/tmp/opencfw-dsp-complete-path').read_text());j=json.loads((d/'build-results.json').read_text());base=j['compile'][0]['command'];k=base.index('/tool/bin/csky-abiv2-elf-gcc');prefix=base[:k];flags=base[k+1:base.index('-c')];rows=[]
for name,macro in [('csky_cfft_radix4by2_q15',False),('csky_bitreversal',True)]:
 p=r/'third-party/upstream/nationalchip-lvp-kws/utility/libdsp/Source/TransformFunctions'/(name+'.c');out=name+('-pure-c' if macro else '')+'.o';cmd=prefix+['/tool/bin/csky-abiv2-elf-gcc']+flags+(['-DFOR_X86_64=1'] if macro else [])+['-c','/repo/'+str(p.relative_to(r)),'-o','/out/'+out];q=subprocess.run(cmd,capture_output=True,text=True);rows.append({'source':str(p.relative_to(r)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr});print(name,q.returncode,flush=True)
objects=['/out/'+p.name for p in d.glob('*.o') if p.name!='csky_bitreversal.o'];cmd=prefix+['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-nostdlib','-nostartfiles','-Wl,-e,csky_rfft_q15','-Wl,-Ttext=0x10003000','-Wl,-Map,/out/complete-c.map','-o','/out/complete-c.elf']+objects;q=subprocess.run(cmd,capture_output=True,text=True);link={'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr}
if q.returncode==0:
 link['sha256']=hashlib.sha256((d/'complete-c.elf').read_bytes()).hexdigest()
 with (d/'complete-c.elf').open('rb') as f:
  e=ELFFile(f);link['undefined_symbols']=[s.name for s in e.get_section_by_name('.symtab').iter_symbols() if s.name and s['st_shndx']=='SHN_UNDEF'];link['defined_symbols']={s.name:hex(s['st_value']) for s in e.get_section_by_name('.symtab').iter_symbols() if s.name.startswith('csky_') and s['st_shndx']!='SHN_UNDEF'}
(d/'link-completion-results.json').write_text(json.dumps({'additional_compile':rows,'link':link,'configuration_note':'FOR_X86_64=1 only exposes unchanged generic C bitreversal definitions on C-SKY target; not a claimed stock SDK recipe.'},indent=2)+'\n');print(json.dumps(link,indent=2),flush=True)

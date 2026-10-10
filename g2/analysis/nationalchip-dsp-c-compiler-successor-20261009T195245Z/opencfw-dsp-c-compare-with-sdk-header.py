from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
r=Path('/Users/kalani/Repo/evenRealities-openCFW');d=r/'g2/analysis/nationalchip-dsp-c-compiler-successor-20261009T195245Z';tool=json.loads((d/'toolchain.json').read_text());image='opencfw/iar-base:10.10.2-local';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=['/opt/homebrew/bin/docker','run','--rm','--network=none','--read-only','--platform','linux/amd64','--mount',f'type=bind,src={tool["extracted_root"]},dst=/tool,readonly','--mount',f'type=bind,src={r},dst=/repo,readonly','--mount',f'type=bind,src={d},dst=/out','--tmpfs','/tmp:rw',image]
version=subprocess.run(base+['/tool/bin/csky-abiv2-elf-gcc','--version'],capture_output=True,text=True);assert version.returncode==0
sources=['TransformFunctions/csky_cfft_radix4_q15.c','TransformFunctions/csky_rfft_q15.c','BasicMathFunctions/csky_shift_q15.c','SupportFunctions/csky_copy_q15.c','SupportFunctions/csky_fill_q15.c']
stock={}
a=json.loads((r/'g2/analysis/nationalchip-dsp-source-rebuild-20261009T194601Z/assembly-results.json').read_text())
for row in a['results']:
 for c in row['comparisons']:stock[c['section']]=c
rows=[]
for rel in sources:
 p=r/'third-party/upstream/nationalchip-lvp-kws/utility/libdsp/Source'/rel;out=d/(p.stem+'.c.o')
 cmd=base+['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-O2','-g','-fno-builtin','-fstrict-volatile-bitfields','-ffunction-sections','-fdata-sections','-I/repo/third-party/upstream/nationalchip-lvp-kws/include/utility/libdsp','-I/repo/third-party/upstream/nationalchip-lvp-kws/include','-I/repo/third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/include','-c','/repo/'+str(p.relative_to(r)),'-o','/out/'+out.name]
 q=subprocess.run(cmd,capture_output=True,text=True);row={'source':str(p.relative_to(r)),'source_sha256':h(p),'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'comparisons':[]}
 if q.returncode==0:
  row['object_sha256']=h(out)
  with out.open('rb') as f:
   e=ELFFile(f)
   for s in e.iter_sections():
    if s.name in stock:
     raw=s.data();ref=stock[s.name];row['comparisons'].append({'section':s.name,'compiled_bytes':len(raw),'compiled_sha256':hashlib.sha256(raw).hexdigest(),'assembly_reference':ref})
 rows.append(row);print(p.name,q.returncode,flush=True)
(d/'c-build-sdk-header-results.json').write_text(json.dumps({'compiler_version':version.stdout,'compiler_version_command':base+['/tool/bin/csky-abiv2-elf-gcc','--version'],'compiler_version_stderr':version.stderr,'image_id':'sha256:af35f7f439b4af1827cdbfffe1f0895540b2aaf8c6a19ff5059e4250047e37d0','recipe':'single DWARF-derived candidate; no added SDK feature macros or flag sweep','results':rows},indent=2)+'\n')

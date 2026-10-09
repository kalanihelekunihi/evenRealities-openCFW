from pathlib import Path
import subprocess,json,hashlib,shutil
from elftools.elf.elffile import ELFFile
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
original=Path('/tmp/opencfw-touch-source/mtb-pdl-cat2-35f1714623cfea682d5e285af80d50416b4c7bbc')
P=R/'g2/analysis/touch-compiler14-successor-2026-10-09/tools/pdl-input'
if not P.exists(): shutil.copytree(original,P,ignore=shutil.ignore_patterns('.git'))
B=R/'g2/analysis/dependency-followup-2026-10-08/touch-source'
source=P/'drivers/source/cy_scb_common.c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='e0cd9973c871649e30cab5e6f4124f1b5bef696eb693c3a796d2c5f08968d3c1'
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()[32:]
flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-DCY8C4046FNI_T412','-ffunction-sections']
inc=['-I/headers','-I/headers/cmsis','-I/pdl/drivers/include','-I/pdl/devices/include','-I/headers/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include']
image='ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'
results=json.loads((O/'results.json').read_text()) if (O/'results.json').exists() else []
for e in json.loads((R/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text()):
    if any(x['tool']['version']==e['version'] for x in results): continue
    out=O/'outputs'/e['version'];out.mkdir(parents=True,exist_ok=True)
    tool=(R/'g2/analysis/touch-compiler14-successor-2026-10-09'/e['gcc']).parents[1]
    common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{P}:/pdl:ro','-v',f'{B}:/headers:ro','-v',f'{out}:/out',image]
    gcc='/tool/bin/arm-none-eabi-gcc'
    def run(args):return subprocess.check_output(common+args,text=True)
    version=run([gcc,'--version']).splitlines()[0]
    for extra in (['-c','/pdl/drivers/source/cy_scb_common.c','-o','/out/public.o'],['-E','/pdl/drivers/source/cy_scb_common.c','-o','/out/public.i'],['-S','/pdl/drivers/source/cy_scb_common.c','-o','/out/public.s'],['-M','/pdl/drivers/source/cy_scb_common.c','-o','/out/public.d']):run([gcc,*flags,*inc,*extra])
    rows=[]
    with (out/'public.o').open('rb') as f:
        elf=ELFFile(f)
        for name,addr,size in [('Cy_SCB_ReadArrayNoCheck',0x9218,56),('Cy_SCB_WriteArrayNoCheck',0x926e,56),('Cy_SCB_WriteDefaultArrayNoCheck',0x92d6,16)]:
            sec=elf.get_section_by_name('.text.'+name);data=sec.data();stock=fw[addr-0x3300:addr-0x3300+size]
            rel=[x.name for x in elf.iter_sections() if x.name in ('.rel'+sec.name,'.rela'+sec.name) and x.num_relocations()]
            assert not rel,rel
            rows.append({'function':name,'stock_address':hex(addr),'stock_bytes':size,'compiled_bytes':len(data),'exact':data==stock,'mismatched_positions':[i for i in range(min(len(data),len(stock))) if data[i]!=stock[i]],'sha256':hashlib.sha256(data).hexdigest(),'relocations':rel})
    deps=(out/'public.d').read_text().replace('\\\n',' ').split(':',1)[1].split()
    hashes={}
    for x in deps:
        p=Path(x)
        for prefix,host in [('/tool/',tool),('/pdl/',P),('/headers/',B)]:
            if x.startswith(prefix):p=host/x[len(prefix):];break
        hashes[x]=sha(p)
    rec={'compiler':version,'tool':e,'flags':flags,'includes':inc,'container':image,'consumed_input_hashes':hashes,'output_hashes':{p.name:sha(p) for p in out.iterdir() if p.is_file()},'functions':rows}
    results.append(rec);print(version,[(x['function'],x['exact'],len(x['mismatched_positions'])) for x in rows],flush=True)
    (O/'results.json').write_text(json.dumps(results,indent=2)+'\n')

from pathlib import Path
import json,hashlib,subprocess,io
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text())[0];T=(R/'g2/analysis/touch-compiler14-successor-2026-10-09'/m['gcc']).parents[1];out=O/'halt-output-attempt2';out.mkdir(exist_ok=True)
common=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{T}:/tool:ro','-v',f'{O}/configure-source:/source:ro','-v',f'{out}:/out','-w','/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'];rows=[]
def command(args):
 p=subprocess.run(common+args,capture_output=True,text=True);rows.append({'argv':common+args,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr});(O/'halt-commands-attempt2.json').write_text(json.dumps(rows,indent=2)+'\n');return p.returncode
status=command(['/bin/sh','/source/libgloss/configure','--host=arm-none-eabi','--build=x86_64-pc-linux-gnu','--no-recursion','--no-create','CC=/tool/bin/arm-none-eabi-gcc','AR=/tool/bin/arm-none-eabi-ar','RANLIB=/tool/bin/arm-none-eabi-ranlib','NM=/tool/bin/arm-none-eabi-nm','CFLAGS=-mcpu=cortex-m0plus -mthumb -Os -ffunction-sections -fdata-sections'])
result={'configure_exit':status,'source_revision':'7923059bff6c120c6fb74b63c7553ea345c0a8f3','limits':'Focused authentic configure-generated header and source-provider comparison, not original vendor full build reproduction. Optimized infinite loop does not imply hardware divide-by-zero.'}
if not status:
 status=command(['/bin/sh','./config.status','config.h']);result['config_status_exit']=status
if not status:
 flags=['-mcpu=cortex-m0plus','-mthumb','-Os','-ffunction-sections','-fdata-sections','-I/out']
 status=command(['/tool/bin/arm-none-eabi-gcc',*flags,'-c','/source/libgloss/libnosys/_exit.c','-o','/out/halt.o']);result['compile_exit']=status
 if not status:
  for option,suffix in [('-E','i'),('-M','d')]:assert command(['/tool/bin/arm-none-eabi-gcc',*flags,option,'/source/libgloss/libnosys/_exit.c','-o','/out/halt.'+suffix])==0
  inputs={}
  for x in (out/'halt.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=O/'configure-source'/x[len('/source/'):] if x.startswith('/source/') else out/x[len('/out/'):] if x.startswith('/out/') else T/x[len('/tool/'):];inputs[x]=sha(p)
  with (out/'halt.o').open('rb') as f:d=ELFFile(f).get_section_by_name('.text._exit').data()
  fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';stock=fw.read_bytes()[32+0xaa40-0x3300:32+0xaa44-0x3300]
  result.update(inputs=inputs,bytes=len(d),exact_stock=d==stock,stock_sha256=hashlib.sha256(stock).hexdigest(),source_sha256=hashlib.sha256(d).hexdigest(),extent='[0xAA40,0xAA44)')
result['outputs']={str(p.relative_to(R)):sha(p) for p in out.iterdir() if p.is_file()};(O/'halt-results-attempt2.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

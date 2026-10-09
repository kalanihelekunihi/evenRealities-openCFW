"""Companion CRT_END provider from the same authentic Makefile contract."""
from pathlib import Path
import json,hashlib,subprocess
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();calls=json.loads((O/'commands.json').read_text());base=next(x['argv'] for x in calls if '/tool/bin/arm-none-eabi-gcc' in x['argv'] and '-c' in x['argv']);rows=[];out=O/'outputs'
for opt,suffix in [('-c','o'),('-E','i'),('-M','d')]:
 argv=[('-DCRT_END' if x=='-DCRT_BEGIN' else opt if x=='-c' else '/out/crtend.'+suffix if x=='/out/crtbegin.o' else x) for x in base];p=subprocess.run(argv,capture_output=True,text=True);rows.append({'argv':argv,'exit_code':p.returncode,'diagnostics':p.stdout+p.stderr});assert p.returncode==0,p.stderr
meta=json.loads((R/'g2/analysis/touch-compiler14-successor-2026-10-09/acquisition.json').read_text())[0];T=(R/'g2/analysis/touch-compiler14-successor-2026-10-09'/meta['gcc']).parents[1];installed=T/'lib/gcc/arm-none-eabi/14.2.1/thumb/v6-m/nofp/crtend.o';comparisons=[]
with installed.open('rb') as f,(out/'crtend.o').open('rb') as g:
 a=ELFFile(f);e=ELFFile(g)
 for s in a.iter_sections():
  if s.name in ['.eh_frame','.tm_clone_table']:
   t=e.get_section_by_name(s.name);comparisons.append({'section':s.name,'archive_bytes':s['sh_size'],'source_bytes':t['sh_size'] if t else None,'raw_equal':bool(t is not None and t.data()==s.data())})
  if s.name=='.eh_frame' and s['sh_size']:
   fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();d=e.get_section_by_name('.eh_frame').data();stock=fw[32+0xb56c-0x3300:32+0xb56c-0x3300+len(d)];comparisons[-1].update(stock_anchor='0xB56C',exact_stock=d==stock,stock_sha256=hashlib.sha256(stock).hexdigest())
result={'calls':rows,'installed_provider_sha256':sha(installed),'source_provider_sha256':sha(out/'crtend.o'),'sections':comparisons,'source_rebuild':True,'source_code_increment':0,'data_terminator_candidate_bytes':4,'limits':'Companion CRT_END source/archive terminator match at the already bound EH-frame anchor. Zero terminator alone is not unique producer evidence or complete exception-runtime registration. Full object identity not claimed.'}
(O/'crtend-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(comparisons,indent=2))

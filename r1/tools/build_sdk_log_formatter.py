#!/usr/bin/env python3
"""Compile authenticated SDK log string-formatter providers."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'sdk-log-formatter';out.mkdir(exist_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());units=[];inputs={};objects=[]
 for stem,roots in [('nrf_log_str_formatter',['nrf_log_std_entry_process','nrf_log_hexdump_entry_process'])]:
  row=next(x for x in sdk['units'] if x['source'].endswith('/'+stem+'.c'));source=ROOT/row['source'];original=source;raw_source=source.read_bytes();start=raw_source.index(b'static void prefix_process(');end=raw_source.index(b'static void postfix_process(',start);generated=out/'nrf_log_str_formatter-selected.c';generated.write_bytes(raw_source[:start]+b'extern void r1_log_prefix_process(nrf_log_str_formatter_entry_params_t *, nrf_fprintf_ctx_t *);\n#define prefix_process r1_log_prefix_process\n'+raw_source[end:]);source=generated;flags=row['command'][1:row['command'].index('-c')];raw=out/(stem+'.o');obj=out/(stem+'-selected.o');dep=out/(stem+'.d');cmd=['clang',*flags,'-O0','-fno-inline','-include',str(ROOT/'r1/source-config/sdk/log_formatter_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True);link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(raw),'-o',str(obj)];subprocess.run(link,check=True);subprocess.run(['arm-none-eabi-objcopy','--strip-unneeded',str(obj)],check=True)
  for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
  u,d=undefined_symbols(obj);units.append(dict(original_source=str(original.relative_to(ROOT)),original_source_sha256=sha(original),prefix_replacement={'offset':start,'length':end-start,'sha256':hashlib.sha256(raw_source[start:end]).hexdigest()},generated_source_sha256=sha(generated),source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u));objects.append(obj)
 inputs[str(original.relative_to(ROOT))]=sha(original)
 config_source=ROOT/'r1/components/board/native_log_prefix.c';config=out/'configuration.o';dep=out/'configuration.d';cmd=['clang',*flags,'-O0','-fno-inline','-MD','-MF',str(dep),'-c',str(config_source),'-o',str(config)];subprocess.run(cmd,check=True);objects.append(config)
 for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 u,d=undefined_symbols(config);units.append(dict(source=str(config_source.relative_to(ROOT)),source_sha256=sha(config_source),command=cmd,compiled=True,object_sha256=sha(config),defined=d,undefined=u))
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 obj=out/'log-formatter.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(obj)],check=True);u,d=undefined_symbols(obj);(out/'report.json').write_text(json.dumps(dict(units=units,inputs=inputs,sdk_report_sha256=sha(sp),selected_object_sha256=sha(obj),remaining_symbols=u,scope='Pinned SDK standard/hexdump/postfix bodies with native prefix replacement and ASCII classifier; printf/calendar/color providers remain dependencies',instruction_identity_proven=False),indent=2)+'\n');print('Log string formatter compiled; remaining:',u)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Compile the complete unchanged pinned Nordic SoftDevice fstorage provider."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PREFIX='r1_sdk_fstorage_sd_'
DATA=['flags','p_cur_op','iget_ctx','fifo','flash_info','sys_obs','req_obs','state_obs']
def main():
 out=BASE/'sdk-fstorage-sd';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());row=next(x for x in sdk['units'] if x['source'].endswith('/nrf_fstorage_sd.c'));source=ROOT/row['source'];flags=row['command'][1:row['command'].index('-c')];raw=out/'nrf_fstorage_sd.o';obj=out/'fstorage-sd.o';dep=out/'nrf_fstorage_sd.d';cmd=['clang',*flags,'-fno-inline',*['-Dm_'+n+'='+PREFIX+n for n in DATA],'-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True)
 names=[n for n,size in functions(raw) if not n.startswith('nrf_')];transform=['arm-none-eabi-objcopy',*[a for n in names for a in ('--redefine-sym',n+'='+PREFIX+n,'--globalize-symbol='+PREFIX+n)],*['--globalize-symbol='+PREFIX+n for n in DATA if n!='fifo'],*['--globalize-symbol='+PREFIX+'fifo_'+n for n in ('inst','data')],str(raw)];subprocess.run(transform,check=True)
 config_source=ROOT/'r1/components/board/sdk_fstorage_sd_configuration.c';config_obj=out/'configuration.o';config_dep=out/'configuration.d';config_cmd=['clang',*flags,'-MD','-MF',str(config_dep),'-c',str(config_source),'-o',str(config_obj)];subprocess.run(config_cmd,check=True)
 link=['arm-none-eabi-ld','-r',str(raw),str(config_obj),'-o',str(obj)];subprocess.run(link,check=True)
 inputs={}
 for n in (dep.read_text()+' '+config_dep.read_text().split(':',1)[1]).replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 u,d=undefined_symbols(obj)
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,object_transforms=[transform],compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],configuration_source=str(config_source.relative_to(ROOT)),configuration_source_sha256=sha(config_source),configuration_command=config_cmd,configuration_object_sha256=sha(config_obj),inputs=inputs,sdk_report_sha256=sha(sp),function_aliases={n:PREFIX+n for n in names},configuration={'queue_capacity':4,'operation_bytes':28,'max_write_chunk':4096,'max_retries':8},scope='Complete unchanged Nordic SoftDevice fstorage implementation; names isolated for shared linking, actual FIFO/atomic/SDH runtime and observer placement remain providers/gates',instruction_identity_proven=False),indent=2)+'\n');print('Full pinned SoftDevice fstorage provider compiled; remaining:',', '.join(u))
if __name__=='__main__':main()

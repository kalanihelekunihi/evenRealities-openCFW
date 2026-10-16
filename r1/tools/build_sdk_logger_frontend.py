#!/usr/bin/env python3
"""Select pinned frontend ring/dequeue/standard/panic bodies with native warning contract."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ROOTS=['nrf_log_init','nrf_log_backend_add','nrf_log_panic','nrf_log_frontend_dequeue','nrf_log_frontend_hexdump',*['nrf_log_frontend_std_'+str(i) for i in range(7)]]
ATOMIC=['nrf_atomic_flag_set','nrf_atomic_flag_clear_fetch','nrf_atomic_u32_add']
def main():
 out=BASE/'sdk-logger-frontend';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());units=[];objects=[];inputs={}
 for stem,roots in [('nrf_log_frontend',ROOTS),('nrf_atomic',ATOMIC),('nrf_ringbuf',['nrf_ringbuf_init'])]:
  row=next(x for x in sdk['units'] if x['source'].endswith('/'+stem+'.c'));source=ROOT/row['source'];flags=row['command'][1:row['command'].index('-c')];raw=out/(stem+'.o');obj=out/(stem+'-selected.o');dep=out/(stem+'.d');extra=['-O0','-fno-inline','-Dm_log_data=r1_sdk_logger_data','-Dm_buffer_mask=r1_sdk_logger_mask','-Dlog_mempool=r1_sdk_logger_mempool','-Dm_log_push_ringbuf=r1_sdk_logger_push_ringbuf','-include',str(ROOT/'r1/source-config/sdk/logger_frontend_contract.h')] if stem=='nrf_log_frontend' else ['-O2','-DNRF_ASSERT_PRESENT=0'];cmd=['clang',*flags,*extra,'-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True);transforms=[]
  if stem=='nrf_log_frontend':
   names=['r1_sdk_logger_push_ringbuf','r1_sdk_logger_push_ringbuf_buf','r1_sdk_logger_push_ringbuf_cb','r1_sdk_logger_data','r1_sdk_logger_mask','r1_sdk_logger_mempool','r1_sdk_logger_mempool_nrf_balloc_cb','r1_sdk_logger_mempool_nrf_balloc_pool_stack','r1_sdk_logger_mempool_nrf_balloc_pool_mem'];transform=['arm-none-eabi-objcopy',*['--globalize-symbol='+n for n in names],str(raw)];subprocess.run(transform,check=True);transforms.append(transform)
  link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(raw),'-o',str(obj)];subprocess.run(link,check=True);strip=['arm-none-eabi-objcopy','--strip-unneeded',str(obj)];subprocess.run(strip,check=True);transforms.append(strip)
  for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
  u,d=undefined_symbols(obj);units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,object_transforms=transforms,compiled=True,object_sha256=sha(obj),defined=d,undefined=u));objects.append(obj)
 assert not set(units[1]['defined'])&{'nrf_atomic_u32_and','nrf_atomic_u32_or','nrf_atomic_u32_fetch_store','nrf_atomic_u32_fetch_or','nrf_atomic_flag_set_fetch'},units[1]['defined']
 config_source=ROOT/'r1/components/board/native_logger_warning.c';config_obj=out/'configuration.o';config_dep=out/'configuration.d';config_cmd=['clang',*flags,'-MD','-MF',str(config_dep),'-c',str(config_source),'-o',str(config_obj)];subprocess.run(config_cmd,check=True);objects.append(config_obj)
 for n in config_dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 selected=out/'logger.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(selected)],check=True);u,d=undefined_symbols(selected)
 (out/'report.json').write_text(json.dumps(dict(units=units,inputs=inputs,sdk_report_sha256=sha(sp),selected_object_sha256=sha(selected),remaining_symbols=u,configuration_source=str(config_source.relative_to(ROOT)),configuration_command=config_cmd,configuration_object_sha256=sha(config_obj),configuration={'NRF_LOG_BUFSIZE':4096,'NRF_LOG_DEFERRED':0,'NRF_LOG_STR_PUSH_BUFFER_SIZE':128,'NRF_ASSERT_PRESENT':0},scope='Unchanged pinned panic/dequeue/standard ring machinery and atomic helpers with native R1 backend-warning contract; memobj/backend/runtime boundaries remain dependencies',instruction_identity_proven=False),indent=2)+'\n');print('Pinned frontend compiled; remaining:',', '.join(u))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Compile pinned upstream CmBacktrace; select initialization with an R1 copy port."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-cmbacktrace-init';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
 reuse_path=BASE/'native-application-entry/upstream-backtrace-reuse.json';reuse=json.loads(reuse_path.read_text());source=ROOT/reuse['source'];assert sha(source)==reuse['source_sha256']=='6e444224af3ef223067849b88f61281ec0661e3f38425e84758bf12be057e01c';assert subprocess.check_output(['git','-C',str(source.parents[1]),'rev-parse','HEAD'],text=True).strip()==reuse['provider']['commit']
 seed_path=BASE/'rtos/report.json';seed=json.loads(seed_path.read_text());command=seed['units'][0]['command'];base=command[1:command.index('-c')];base=['-I'+str(ROOT/'r1/source-config/runtime/cmbacktrace'),'-I'+str(source.parent),*base,'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-O0','-fno-inline','-fshort-enums','-ffunction-sections','-fdata-sections']
 inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),str(reuse_path.relative_to(ROOT)):sha(reuse_path)};units=[]
 for src,name,extra in [(source,'cm_backtrace', ['-DCMB_USER_CFG','-Dstrncpy=r1_cmb_copy_name']),(ROOT/'r1/components/runtime/native_cmbacktrace_copy_port.c','copy_port',[])]:
  obj=out/(name+'.o');dep=out/(name+'.d');cmd=['clang',*base,*extra,'-MD','-MF',str(dep),'-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
  for item in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(item);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
  u,d=undefined_symbols(obj);units.append(dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=u,defined=d))
 selected=out/'cmbacktrace-init.o';select=['arm-none-eabi-ld','-r','--gc-sections','--undefined=cm_backtrace_init',str(out/'cm_backtrace.o'),str(out/'copy_port.o'),'-o',str(selected)];subprocess.run(select,check=True)
 copy_report=BASE/'native-libc-sequences/report.json';copy=json.loads(copy_report.read_text());copy_obj=copy_report.parent/'native_libc_sequences.o';assert sha(copy_obj)==copy['units'][0]['object_sha256'];copy_selected=out/'native-strncpy.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_native_strncpy',str(copy_obj),'-o',str(copy_selected)],check=True)
 linked=out/'cmbacktrace-init-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(selected),str(copy_selected),'-o',str(linked)],check=True);unresolved,defined=undefined_symbols(linked)
 assert unresolved==['r1_cmb_code_end','r1_cmb_code_start','r1_cmb_stack_end','r1_cmb_stack_start','r1_retained_log_printf_sink'],unresolved
 report=dict(units=units,inputs=inputs,selected_object_sha256=sha(selected),selected_symbols=undefined_symbols(selected)[1],linked_sha256=sha(linked),undefined_symbols=unresolved,defined_symbols=defined,provider_reports={'native-libc-sequences/report.json':sha(copy_report)},provider_object_sha256=sha(copy_obj),selection_command=select,upstream_source=str(source.relative_to(ROOT)),upstream_source_sha256=sha(source),upstream_license=str((source.parents[1]/'LICENSE').relative_to(ROOT)),upstream_license_sha256=sha(source.parents[1]/'LICENSE'),upstream_commit=reuse['provider']['commit'],exact_vendor_checkout_proven=False,full_upstream_translation_unit_compiled=True,selected_native_scope='cm_backtrace_init only; other fault/unwind bodies compiled but not native-admitted here',application_linked=False,original_instruction_identity=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Pinned upstream CmBacktrace compiled; selected init links to source copy provider; four linker bounds and retained log provider remain')
if __name__=='__main__':main()

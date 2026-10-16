#!/usr/bin/env python3
"""Build the pinned, unmodified Newlib formatter candidate; retain closure gates."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vendor=ROOT/'third-party/upstream/newlib-stdio-3.3.0';out=ROOT/'r1/research/source-build/newlib-stdio';out.mkdir(exist_ok=True)
    (out/'report.json').unlink(missing_ok=True)
    pinfile=vendor/'provenance.json';pin=json.loads(pinfile.read_text())
    assert pin['commit']=='6d79e0a58866548f435527798fbd4a6849d05bc7'
    for row in pin['files']:assert sha(vendor/row['path'])==row['sha256'],row['path']
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=gnu11','-fshort-enums','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include')]
    for part in ['stdio','stdlib','locale']:flags+=['-I'+str(vendor/'newlib/libc'/part)]
    flags+=['-I'+str(vendor/'newlib/libm/common')]
    units=[('snprintf','newlib/libc/stdio/snprintf.c',[]),('svfprintf','newlib/libc/stdio/vfprintf.c',['STRING_ONLY']),('svfiprintf','newlib/libc/stdio/vfprintf.c',['STRING_ONLY','INTEGER_ONLY']),('impure','newlib/libc/reent/impure.c',[])]
    for path in ['newlib/libc/ctype/ctype_.c','newlib/libc/stdlib/mbtowc_r.c','newlib/libc/stdlib/wctomb_r.c','newlib/libc/stdlib/dtoa.c','newlib/libc/stdlib/mprec.c','newlib/libc/locale/localeconv.c','newlib/libc/locale/locale.c','newlib/libc/string/memchr.c','newlib/libc/string/strncpy.c','newlib/libm/common/s_fpclassify.c','newlib/libm/math/s_frexp.c']:units.append((Path(path).stem,path,[]))
    for name in ['MALLOC','FREE','REALLOC','CALLOC']:units.append(('heap-'+name.lower(),'newlib/libc/stdlib/mallocr.c',['INTERNAL_NEWLIB','DEFINE_'+name]))
    inputs={str(pinfile.relative_to(ROOT)):sha(pinfile),str(Path(__file__).resolve().relative_to(ROOT)):sha(Path(__file__))};rows=[];objects=[]
    for name,path,defines in units:
        source=vendor/path;obj=out/(name+'.o');dep=out/(name+'.d');cmd=['clang',*flags,*['-D'+d for d in defines],'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)]
        subprocess.run(cmd,check=True)
        for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            p=Path(p);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
        unresolved,defined=undefined_symbols(obj);rows.append(dict(source=path,defines=defines,command=cmd,object_sha256=sha(obj),undefined=unresolved,defined=defined));objects.append(obj)
    llvm=ROOT/'third-party/upstream/llvm-compiler-rt-format-20.1.8';llvmpin=llvm/'provenance.json'
    inputs[str(llvmpin.relative_to(ROOT))]=sha(llvmpin)
    for row in json.loads(llvmpin.read_text())['files']:assert sha(llvm/row['path'])==row['sha256'],row['path']
    for name in ['adddf3','subdf3','muldf3','divdf3','comparedf2','fixdfsi','floatsidf','floatunsidf','fp_mode']:
        source=llvm/(name+'.c');obj=out/('llvm-'+name+'.o');dep=out/('llvm-'+name+'.d');cmd=['clang',*flags,'-DCOMPILER_RT_ARMHF_TARGET','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)]
        subprocess.run(cmd,check=True)
        for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            p=Path(p);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
        unresolved,defined=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),command=cmd,object_sha256=sha(obj),undefined=unresolved,defined=defined));objects.append(obj)
    source=ROOT/'r1/components/runtime/newlib_double_comparisons.c';obj=out/'double-comparisons.o'
    cmd=['clang',*flags,'-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
    inputs[str(source.relative_to(ROOT))]=sha(source)
    unresolved,defined=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),command=cmd,object_sha256=sha(obj),undefined=unresolved,defined=defined));objects.append(obj)
    reused=[]
    for directory,names in [('runtime',['memcpy','memset','strcmp','strlen']),('runtime-memmove',['memmove']),('integer-runtime',['integer-runtime'])]:
        rp=out.parent/directory/'report.json';provider=json.loads(rp.read_text());inputs[str(rp.relative_to(ROOT))]=sha(rp)
        for path,digest in provider['inputs'].items():
            assert sha(ROOT/path)==digest,path
            inputs[path]=digest
        for name in names:
            obj=out.parent/directory/(name+'.o')
            expected=provider.get('relocatable_sha256') if name=='integer-runtime' else next(row['object_sha256'] for row in provider['units'] if Path(row['source']).stem==name)
            assert sha(obj)==expected,str(obj)
            objects.append(obj);reused.append(dict(object=str(obj.relative_to(ROOT)),sha256=sha(obj),report_sha256=sha(rp)))
    linked=out/'newlib-stdio.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True)
    unresolved,_=undefined_symbols(linked)
    report=dict(status='compiled-partial-candidate',commit='6d79e0a58866548f435527798fbd4a6849d05bc7',units=rows,reused_source_providers=reused,inputs=inputs,remaining_symbols=unresolved,relocatable_sha256=sha(linked),native_formatter_equivalence_proven=False,instruction_identity_proven=False,gates=['Resolve all allocation, locale, math and EABI dependencies from attributable C sources.','Compare generic formatting against authenticated native 0x38080/0x43080, including varargs, truncation and floating point.','Prove native state ownership, ABI and byte identity before whole-image admission.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(units=len(rows),remaining_symbols=unresolved)))
if __name__=='__main__':main()

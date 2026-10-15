#!/usr/bin/env python3
"""Compile only the admitted public Goodix source subset; never inspect archives."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import struct
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols

ROOT=Path(__file__).resolve().parents[2]
PIN='2c0034a23b675a5f9a29e4a47e8b504c7a88e321'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    tree=ROOT/'third-party/upstream/goodix-gh3x2x';base=tree/'gh3x2x'
    assert (tree/'.git').exists()
    assert subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip()==PIN
    assert not subprocess.check_output(['git','-C',str(tree),'status','--porcelain'],text=True).strip()
    assert sha(base/'LICENSE')=='dfb94b7725971b1696299c6d9fd36b8a447c40c1a9c9e89a8a392377f9823226'
    make=(ROOT/'r1/config-recovered/sdk-source-list.mk').read_text()
    block=make.split('GOODIX_SUBSET_SOURCES :=',1)[1].split('SRC_FILES +=',1)[0]
    variables={'GOODIX_DEMOCODE_ROOT':base,'GOODIX_DRIVER_DIR':base/'demo_code/demo_kernel_code/driver',
               'GOODIX_KERNEL_DIR':base/'demo_code/demo_kernel_code/kernel','GOODIX_MODULE_DIR':base/'demo_code/demo_kernel_code/module'}
    sources=[]
    for var,relative in re.findall(r'\$\((GOODIX_[A-Z_]+)\)/([^\s\\]+\.c)',block):
        source=variables[var]/relative
        assert source.suffix=='.c' and source.is_file(),source
        assert '/demo_algo_code/' not in str(source) and '/gh_protocol/' not in str(source)
        sources.append(source)
    # The expanded reconstruction scope also consumes the public configuration
    # unit with per-entry matches (0x2AEDC, 0x29F88, 0x2A630, 0x2ACF4, etc.).
    sources.append(base/'demo_code/demo_algo_code/goodix_algo_application/src/gh3x2x_demo_algo_config.c')
    include_block=make.split('INC_FOLDERS +=',1)[1].split('OPT :=',1)[0]
    includes=[ROOT/'r1/source-config/goodix']
    includes += [variables[var]/relative for var,relative in re.findall(r'\$\((GOODIX_[A-Z_]+)\)/([^\s\\]+)',include_block)]
    includes += [variables[var] for var in ('GOODIX_DRIVER_DIR','GOODIX_KERNEL_DIR','GOODIX_MODULE_DIR')]
    # Driver public headers live in driver/inc, included explicitly by the seed.
    output=ROOT/'r1/research/source-build/goodix';output.mkdir(parents=True,exist_ok=True)
    (output/'report.json').unlink(missing_ok=True)
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
           '-ffreestanding','-fno-builtin','-fno-strict-aliasing','-std=c11','-Os','-ffunction-sections','-fdata-sections',
           '-Wno-builtin-macro-redefined','-D__DATE__="Oct 15 2026"','-D__TIME__="00:00:00"',
           '-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),
           *['-I'+str(p) for p in dict.fromkeys(includes)]]
    application=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
    image=application.read_bytes()
    assert sha(application)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    configuration=image[0xad160-0x27000:0xad1ac-0x27000]
    assert hashlib.sha256(configuration).hexdigest()=='afa9429b02ee229c0363000ebc02be13b51ec6ac0e5b9c06d621947d65eb7fe5'
    coefficients=struct.unpack_from('<iii',configuration,16)
    assert coefficients==(-156022,-42041,1066184)
    rows=[]
    for i,original in enumerate(sources):
        source=original
        if original.name=='goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c':
            contents=original.read_bytes()
            for old,new in zip((-124026,-59505,1043941),coefficients):
                assert contents.count(str(old).encode())==1
                contents=contents.replace(str(old).encode(),str(new).encode())
            contents+=b'\n#include <stddef.h>\n_Static_assert(sizeof(goodix_spo2_config)==76,"stock SpO2 config size");\n'
            for field,offset in [('cali_coef_a2',16),('cali_coef_a1',20),('cali_coef_a0',24)]:
                contents+=f'_Static_assert(offsetof(goodix_spo2_config,{field})=={offset},"stock {field} offset");\n'.encode()
            source=output/'stock_spo2_config.c';source.write_bytes(contents)
        obj=output/f'{i:02d}_{source.stem}.o';obj.unlink(missing_ok=True)
        command=['clang',*flags,'-c',str(source),'-o',str(obj)]
        result=subprocess.run(command,capture_output=True,text=True)
        row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),original_source=str(original.relative_to(ROOT)),original_source_sha256=sha(original),command=command,
                 compiled=result.returncode==0,diagnostics=result.stderr)
        if row['compiled']:
            undefined,defined=undefined_symbols(obj);symbols=functions(obj)
            row.update(object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(symbols))
        rows.append(row)
    definitions={s for row in rows for s in row.get('defined',[])}
    report=dict(schema=1,application_sha256=sha(application),stock_spo2_configuration_sha256=hashlib.sha256(configuration).hexdigest(),stock_calibration_coefficients=list(coefficients),upstream_pin=PIN,license_sha256=sha(base/'LICENSE'),units=rows,
                compiled=sum(row['compiled'] for row in rows),total=len(rows),
                unresolved=sorted({s for row in rows for s in row.get('undefined',[])}-definitions),
                compiler_version=subprocess.check_output(['clang','--version'],text=True),
                overlay_sha256=sha(ROOT/'r1/source-config/goodix/gh_demo_config.h'),
                version_timestamp='Oct 15 2026 00:00:00 (candidate-only deterministic value)',
                stock_configuration_proven=False,image_linked=False,byte_identity_proven=False,
                limitations=['Only public C sources compile, including the later source-correlated algorithm-configuration unit. No Goodix binary archive is inspected or linked.',
                             'Vendor defaults other than the evidence-backed all-source FIFO selection remain candidate configuration.',
                             'Candidate version date/time is deterministic and is not a recovered stock timestamp.',
                             'External algorithm and R1 HAL contracts remain unresolved until independently supplied and validated.'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Goodix source-only candidate units compiled: {report['compiled']}/{report['total']}")
    for row in rows:
        if not row['compiled']:print(row['source']+'\n'+row['diagnostics'][:2500])
    print('Remaining external symbols:',', '.join(report['unresolved']))
    return 0 if all(row['compiled'] for row in rows) else 1


if __name__=='__main__':raise SystemExit(main())

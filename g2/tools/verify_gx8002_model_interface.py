#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Require byte-exact C reconstruction of the codec model interface cluster."""
import argparse
import json
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'components/shared/gx8002/runtime_gx8002_model_interface.c'
# Reviewed callable bodies; the retained task-copy wrapper is deliberately
# excluded. These are package offsets, not inferred VMAs. The fourth element
# is the trailing zero-byte trap (0x0000 `bkpt`) GCC emits after a handful of
# these leaf getters to hold 4-byte alignment for the next symbol; it is not
# part of the compiled body but is claimed here as CD-012 generated fill
# because it immediately follows the function it pads and is authenticated
# byte-for-byte against the stock envelope in verify().
FUNCTIONS=(('LvpModelGetCmdSize',0x12180,6,2),('LvpModelGetWeightSize',0x12188,8,0),
           ('LvpModelGetOpsSize',0x12190,4,0),('LvpModelGetDataSize',0x12194,6,2),
           ('LvpModelGetTmpSize',0x1219c,4,0),('LvpCTCModelInitSnpuTask',0x121b4,56,0),
           ('LvpCTCModelGetSnpuOutBuffer',0x121ec,8,0),('LvpCTCModelGetSnpuFeatsBuffer',0x121f4,2,2),
           ('LvpCTCModelGetSnpuStateBuffer',0x121f8,6,2),('LvpCTCModelGetSnpuFeatsDim',0x12200,6,2))


def verify(prefix,sdk,output):
    if subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip()!=SDK_COMMIT:
        raise ValueError('SDK revision changed')
    name='include/driver/gx_snpu.h'
    digest=subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD:'+name],text=True).strip()
    header=authenticated_blob(sdk/name,digest)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('firmware oracle changed')
    output.mkdir(parents=True,exist_ok=True)
    (output/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    obj=output/'runtime_gx8002_model_interface.o'
    subprocess.run([str(prefix/'csky-unknown-elf-gcc'),*FLAGS,'-I',str(output),'-I',str(sdk/'include'),
                    '-c',str(SOURCE),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj))
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unexpected undefined symbol')
    sections=[s for s in elf.sections if s['flags']&4 and s['size']]
    if {s['name'] for s in sections}!={'.text.'+name for name,_,_,_ in FUNCTIONS}:
        raise ValueError('model interface function inventory changed')
    records=[]
    for symbol,offset,size,fill in FUNCTIONS:
        section=next(s for s in sections if s['name']=='.text.'+symbol)
        payload=elf.contents(section)
        if len(payload)!=size or payload!=stock[offset:offset+size] or elf.relocations(section['index']):
            raise ValueError('model interface no longer exactly matches stock: '+symbol)
        if offset%section['align']:raise ValueError('literal pool alignment mismatch')
        envelope=size+fill
        if fill and stock[offset+size:offset+envelope]!=bytes(fill):
            raise ValueError('trailing fill after '+symbol+' is not an authenticated zero trap')
        records.append({'symbol':symbol,'compiled_bytes':size,'compiled_sha256':sha(payload),
                        'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':envelope,
                                              'sha256':sha(stock[offset:offset+envelope]),'region':'image_a_xip_text'}]})
    report={'source_sha256':sha(SOURCE.read_bytes()),'sdk_commit':SDK_COMMIT,'compile_flags':FLAGS,
            'upstream_header':{'path':name,'git_blob':digest,'sha256':sha(header)},
            'configuration':{'CONFIG_ARCH_GRUS':1},'functions':records,
            'compiled_function_bytes':sum(size for _,_,size,_ in FUNCTIONS),
            'saved_task_address':'0x2002e85c','task_size':32,'source_admitted_as_model_data':False,
            'firmware_bytes_emitted':0,'hardware_qualified':False,
            'limits':['Byte-exact interface code does not reconstruct the model graph or accelerator commands.',
                      'Saved-task initialization/copy and its other callers remain separate recovery work.']}
    (output/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prefix',type=Path,default=ROOT/'build/csky-macos/install/bin')
    p.add_argument('--sdk',type=Path,default=ROOT/'build/upstream-nationalchip-lvp-kws')
    p.add_argument('--output',type=Path,default=ROOT/'build/gx8002-model-interface-source')
    a=p.parse_args();print(json.dumps(verify(a.prefix.resolve(),a.sdk.resolve(),a.output.resolve()),indent=2))


if __name__=='__main__':main()

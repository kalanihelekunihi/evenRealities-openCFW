#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build typed wakeword parameters without using stock as a source generator."""
import json,re,shutil,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_logging import check_paths
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='include/lvp_param.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    text=authenticated_blob(sdk/rel,blob).decode();matches=re.findall(r'typedef struct \{[^}]*\} LVP_KWS_PARAM;',text)
    if len(matches)!=1:raise ValueError('parameter type extraction')
    out=ROOT/'build/gx8002-board';header=out/'wakeword-upstream-types.h'
    header.write_text('/* Exact type from authenticated upstream lvp_param.h. */\n'+matches[0]+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_wakeword_parameters.c';obj=out/'wakeword-parameters.o';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-I'+str(out),'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj));name='.data.open_cfw_gx8002_wakeword_parameters';sec=next(s for s in elf.sections if s['name']==name);payload=elf.contents(sec)
    stock=IMAGE.read_bytes();offset=0x18c90
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if len(payload)!=176 or elf.relocations(sec['index']) or payload!=stock[offset:offset+176]:raise ValueError('wakeword parameter layout/payload')
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-PARAMETERS-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(obj,output/'wakeword-parameters.o');shutil.copyfile(notice,output/notice.name)
    return {'functions':[{'symbol':'open_cfw_gx8002_wakeword_parameters','section_name':name,'ownership_kind':'generated_source_data',
      'compiled_bytes':176,'compiled_sha256':sha(payload),'stock_occurrences':[{'symbol':'open_cfw_gx8002_wakeword_parameters',
      'package_offset':offset,'bytes':176,'sha256':sha(stock[offset:offset+176]),'region':'image_a_sram_data'}]}],
      'notice_sha256':sha(notice.read_bytes()),'source_sha256':sha(source.read_bytes()),'upstream_type_sha256':sha(header.read_bytes()),'sdk_commit':SDK_COMMIT,
      'upstream_header_git_blob':blob,'upstream_header_sha256':sha(text.encode()),'flags':FLAGS,'source_admitted':True,'hardware_qualified':False,
      'limits':['Two typed parameter records only. Vocabulary label54 interpretation, model weights and complete decoding remain separate recovery work. Table fields are source-defined; stock is a comparison oracle only.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-wakeword-parameters-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')

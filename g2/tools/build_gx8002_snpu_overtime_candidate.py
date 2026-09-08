#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link diagnostics/restart C and reviewed literal strings; no admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
DELTA=0x101f6a74
FUNCTIONS=[('open_cfw_gx8002_snpu_dump_words',0xf064,68),('open_cfw_gx8002_snpu_overtime_reset',0xf0a8,188)]
MESSAGES=[('open_cfw_snpu_dump_word',0x1020ac0e),('open_cfw_snpu_overtime_addresses',0x1020ac16),('open_cfw_snpu_overtime_before',0x1020ac5c),('open_cfw_snpu_overtime_command',0x1020ac7a),('open_cfw_snpu_overtime_type',0x1020ac91)]
BINDINGS={'printf':0x10206c24,'open_cfw_gx8002_max_list_newline':0x1020b7c2,'open_cfw_snpu_overtime_words':0x20027350,'open_cfw_gx8002_npu_get_base_addr':0x102058b4,'open_cfw_gx8002_npu_get_cur_cmd_addr':0x102058c4,'open_cfw_gx8002_npu_get_over_cmd_addr':0x10205860,'open_cfw_gx8002_npu_get_task_head':0x102058a4,'open_cfw_gx8002_npu_disable':0x10205600,'open_cfw_gx8002_npu_reset':0x10205880,'open_cfw_gx8002_npu_regs_init':0x10205950,'open_cfw_gx8002_npu_set_task_head':0x10205898,'open_cfw_gx8002_npu_enable':0x102055f4}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='drivers_lib/snpu/grus/snpu.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('overtime stock identity')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_snpu_overtime_reset.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    obj=out/'snpu-overtime-candidate.o';subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(obj)],check=True)
    script=out/'snpu-overtime-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {o+DELTA:#x} : {{ *(.text.{n}) }}\n' for n,o,size in FUNCTIONS)+''.join(f'.rodata.{n} {a:#x} : {{ *(.rodata.{n}) }}\n' for n,a in MESSAGES)+'}\n'+''.join(f'{n} = {a:#x};\n' for n,a in BINDINGS.items()))
    path=out/'snpu-overtime-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(path)],check=True);elf=Elf32(path.read_bytes(),str(path));rows=[]
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('overtime unresolved symbol')
    for name,offset,size in FUNCTIONS:
        sec=next(s for s in elf.sections if s['name']=='.text.'+name);data=elf.contents(sec)
        if elf.relocations(sec['index']):raise ValueError('overtime relocation')
        rows.append({'symbol':name,'section_name':sec['name'],'package_offset':offset,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'fits':len(data)<=size})
    for name,address in MESSAGES:
        sec=next(s for s in elf.sections if s['name']=='.rodata.'+name);data=elf.contents(sec);offset=address-DELTA
        if not data.endswith(b'\0') or data!=stock[offset:offset+len(data)]:raise ValueError('overtime literal mismatch '+name)
        rows.append({'symbol':name,'section_name':sec['name'],'package_offset':offset,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_envelope_bytes':len(data),'stock_sha256':sha(data),'fits':True,'ownership_kind':'generated_source_data'})
    (out/'snpu-overtime-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle)},'source_sha256':sha(source.read_bytes()),'flags':flags,'bindings':BINDINGS,'regions':rows,'source_admitted':False,'limits':['Candidate only. Need diagnostic load/printf sequences, helper mutations, head-selection paths, restart ordering, register reloads and ABI checks. Existing newline ownership reused. Command address validity and state layout remain separate.']}
    (ROOT/'docs/research/gx8002-snpu-overtime-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))

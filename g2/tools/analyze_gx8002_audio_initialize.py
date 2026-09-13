# SPDX-License-Identifier: MIT
"""Authenticate audio initializer boundary and SDK dependency evidence."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def analyze():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Initializer stock identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_in/v2.0/audio_in.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    data=authenticated_blob(sdk/rel,blob);elf=Elf32(data,rel);section=next(s for s in elf.sections if s['name']=='.text.gx_audio_in_init')
    return {'sdk_commit':SDK_COMMIT,'sdk_blob':blob,'sdk_sha256':sha(data),'sdk_relocations':elf.relocations(section['index']),'package_offset':0xdd70,'envelope_bytes':416,'stock_sha256':sha(stock[0xdd70:0xdf10]),
      'state_base':0x20027330,'state_bytes':28,
      'state_layout':{'input_mask':0,'output_mask':4,'config_callback':8,'record_callback':12,'update_callback':16,'engvad_callback':20,'fftvad_callback':24},
      'calls':[{'name':'gx_clock_set_module_enable','address':0x10025080,'arguments':[3,1]},{'name':'memset','address':0x102099cc,'arguments':[0x20027330,0,28]},{'name':'_ain_reset','address':0x10203c88},{'name':'config_callback','indirect':True,'return_ignored':True},{'name':'gx_request_irq','address':(0xffe2eac8+0x101f6a74)&0xffffffff,'arguments':[2,0x10025e48,0]}],
      'observations':['Clock, clear-state, reset and initial MMIO precede required config-callback null check.','Callback publication order: config, optional update, optional record, optional engvad, optional fftvad.','Record callback presence gates output-mask interrupt bits0/1/2.','Input-mask snapshot controls SADC/PDM/I2S starts. PDM selector low4 must be<2; I2S selector low4 must be<8.','Channel-enable reads and writes remain separate; input shutdown controls clear bits7/15 at base0 and bit31 at base4.'],
      'source_admitted':False,'hardware_qualified':False,'limits':['Dependency names from pinned SDK relocation evidence; source implementation and nested execution qualification pending.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-audio-initialize-analysis.json').write_text(json.dumps(r,indent=2)+'\n');print('Initializer dependency evidence authenticated')

# SPDX-License-Identifier: MIT
"""Literal reference inventory; not a complete data-flow or producer proof."""
import json,struct
from analyze_g2_codec_stage2_sections import analyze as section_map, SEG2_OFF
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha


SDK_EVIDENCE = {
    'arch/soc/grus/include/soc_config.h': 'abda275af6aee96ad676c190e2a72363a79595413336371fced4450f8df76809',
    'arch/soc/grus/link.ld': '1dc73b74c4b5962a848693ab857e90d34115489a8a7e499897533ad786ff77be',
    'arch/soc/grus/spl/spl.c': 'f3690694fff309c0118579baedb860b1d47c6de3cfb227a977242249568bb56b',
}


def mapped_offset(address, layout, sdk):
    """Resolve the data alias using authenticated SDK and stock section evidence."""
    for rel, digest in SDK_EVIDENCE.items():
        if sha((sdk/rel).read_bytes()) != digest:
            raise ValueError('SDK memory-map evidence changed: '+rel)
    data = layout['image_a']['stage2']['sram_data']
    if (data['flash'], data['iram'], data['size']) != (
            '[0xEF70, 0xF804)', '[0x100264E8, 0x10026D7C)', 0x894):
        raise ValueError('Stock initialized-data section changed')
    # soc_config.h defines matching IRAM/DRAM offsets; link.ld reserves the
    # text span in DRAM before initialized data. SPL loads via DRAM and executes IRAM.
    dram_start = 0x100264e8 + (0x20000000-0x10000000)
    if address & 3 or not dram_start <= address <= dram_start+data['size']-4:
        raise ValueError('State word outside initialized data or misaligned')
    return SEG2_OFF+0xef70+(address-dram_start)


def analyze():
    image=IMAGE.read_bytes()
    if sha(image)!=IMAGE_SHA:raise ValueError('State inventory stock hash')
    data_region=image[0x184fc:0x18d90]
    data_sha='e0a88003909bb45ae966bfedcbf6e21a5bc83137d26bd36c7f81114fa0034384'
    if sha(data_region)!=data_sha:raise ValueError('Image-A initialized-data region hash')
    offset=mapped_offset(0x20026c70,section_map(),ROOT/'build/upstream-nationalchip-lvp-kws')
    addresses=(0x20026c70,0x20026c00,0x20026c60,0x20026c68,0x20026c6c,0x20026c74,0x20026c78,0x20026000)
    hits={hex(a):[i for i in range(len(image)-3) if image[i:i+4]==struct.pack('<I',a)] for a in addresses}
    return {'image_sha256':IMAGE_SHA,'literal_hits':hits,
            'candidate_data_mapping':{'runtime_minus_package':0x20026c70-offset,
                'package_offset':offset,'word':struct.unpack_from('<I',image,offset)[0],
                'section_mapping_verified_here':True,
                'sdk_memory_map_sha256':SDK_EVIDENCE,
                'authenticated_initialized_data_region':{'start':0x184fc,'end':0x18d90,'sha256':data_sha},
                'word_within_authenticated_region':True,
                'unresolved':'Producer data flow and runtime lifecycle' },
            'source_admitted':False,'lifecycle_established':False,
            'limits':['All byte alignments scanned for selected literal words only. Computed addresses, pointers through structures, DMA and external updates are not excluded. Mapping is supported by authenticated stock section arithmetic and SDK memory layout; physical hardware behavior remains unqualified.']}


if __name__=='__main__':
    report=analyze();(ROOT/'docs/research/gx8002-gsensor-state-references.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Gsensor literal inventory written; lifecycle remains unresolved')

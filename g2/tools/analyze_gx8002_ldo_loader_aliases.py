# SPDX-License-Identifier: MIT
"""Measure earlier-image LDO aliases after the normal backup loader copy."""
import json
import subprocess
from analyze_gx8002_backup_ldo_references import verify as references
from verify_gx8002_backup_memset_loader import execute
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=references();image=IMAGE.read_bytes();assert sha(image)==IMAGE_SHA
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    code=decode(subprocess.check_output([tool,'-D','--start-address=0x396a0','--stop-address=0x396ee',str(wrapper)],text=True))
    addresses=[r['runtime_address'] for r in evidence['strings']]+[evidence['jump_table']['runtime_address']]
    cases=0;observations=[]
    for mode in (0,1,0xffffffff,0xaabbccdc):
        for seed in (0,91,0xffffffff):
            result,calls,memory=execute(code,image,mode,seed)
            assert result==0 and calls==[['read',0x323b0,0x2002ffec,4],['read',0x323b4,0x10003000,0x1408c],['entry',0x10003100]]
            for address in addresses:
                earlier=address-0x10000000+0x50;backup=address-0x10003000+0x3b940
                value=memory[address];assert value==int.from_bytes(image[backup:backup+4],'little')
                assert value!=int.from_bytes(image[earlier:earlier+4],'little')
                if cases==0:observations.append({'runtime_address':address,'earlier_offset':earlier,'backup_offset':backup,'earlier_word':int.from_bytes(image[earlier:earlier+4],'little'),'loaded_word':value})
            cases+=1
    return {'reference_evidence':evidence,'normal_loader_cases':cases,'observations':observations,'earlier_data_replaced_before_entry':True,'cross_image_lifetime_resolved':False,'limits':['The normal stock loader already replaces all five earlier-image data addresses before its backup-entry call. Earlier strings/table cannot retain their original meaning during backup execution even without an LDO patch. This establishes overwrite ordering, not full caller/interrupt lifetime. Special loader mode and physical cache/interrupt behavior remain outside these modeled flash-read cases.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-ldo-loader-aliases.json').write_text(json.dumps(r,indent=2)+'\n');print(r['normal_loader_cases'],'normal loader alias cases passed')

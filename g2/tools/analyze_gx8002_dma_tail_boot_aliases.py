# SPDX-License-Identifier: MIT
"""Classify DMA-tail address matches as UART boot switch-table references."""
import json,struct,subprocess,zlib
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    image=IMAGE.read_bytes();assert sha(image)==IMAGE_SHA
    kind,size,offset,crc=struct.unpack_from('<IIII',image,16);assert (kind,size,offset)==(1,38236,48)
    payload=image[offset:offset+size];assert zlib.crc32(payload)==crc
    stage1,stage2=struct.unpack_from('>I',payload,8)[0],struct.unpack_from('>I',payload,16)[0]
    assert stage1==0x2800 and stage2==0x6d3c and len(payload)==32+stage1+stage2
    package_base=offset+32+stage1;runtime_base=0x10002800
    assert package_base==0x2850 and struct.unpack_from('<I',image,package_base)[0]==runtime_base+0x100
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==image
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-D','--start-address=0x4b10','--stop-address=0x4c40',str(path)],text=True))
    assert code[0x4b1c][:2]==('lrw','r1, 0x10008174') and code[0x4bac][:2]==('lrw','r2, 0x100081c0')
    assert code[0x4b18][:2]==('cmphsi','r2, 19') and code[0x4ba6][:2]==('cmphsi','r3, 19')
    tables=[(0x10008174,19,0x4b1c),(0x100081c0,19,0x4bac)]
    report=json.loads((ROOT/'docs/research/gx8002-backup-replacement-tails.json').read_text());matches=next(r for r in report['tails'] if r['function']=='dma_configure')['runtime_pointers'];rows=[]
    for match in matches:
        owner=next((t for t in tables if package_base+t[0]-runtime_base<=match['offset']<package_base+t[0]-runtime_base+t[1]*4),None);assert owner
        target=package_base+match['value']-runtime_base
        assert target in code and 0x2850<=target<0x958c
        rows.append({**match,'boot_table_runtime':owner[0],'boot_dispatch_pc':owner[2],'boot_target_package':target,'boot_target_instruction':list(code[target][:2])})
    assert len(rows)==14
    result={'image_sha256':IMAGE_SHA,'boot_stage2_package_base':package_base,'boot_stage2_runtime_base':runtime_base,'classified_matches':rows,'reclaim_admitted':False,'limits':['These exact words are boot-stage switch-table targets under authenticated container/vector mapping. This explains the numeric overlap with backup SRAM code.','Classification does not globally exclude cross-image references or establish loader-safe tail reuse. No bytes changed.']}
    (ROOT/'docs/research/gx8002-dma-tail-boot-aliases.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(len(analyze()['classified_matches']))

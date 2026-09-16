# SPDX-License-Identifier: MIT
"""Identify earlier-image data aliases within the backup LDO address range."""
import json
import subprocess
from analyze_gx8002_double_wrapper_references import analyze
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode


def verify():
    census=analyze(0x40a34,0x40a74);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    def code(a,b):return decode(subprocess.check_output([tool,'-D',f'--start-address={a:#x}',f'--stop-address={b:#x}',str(wrapper)],text=True))
    assert [w['offset'] for w in census['stored_address_words']]==[0x4548,0x4ab0,0x9254,0x9264,0x9274]
    strings=[]
    for off,address,value in ((0x4548,0x10008114,b'level timout invalid\n'),(0x9254,0x100080f4,b'p25q80l'),(0x9264,0x100080fc,b'en25s20a'),(0x9274,0x10008108,b'en25s40a')):
        assert int.from_bytes(stock[off:off+4],'little')==address
        target=address-0x10000000+0x50
        assert stock[target:target+len(value)+1]==value+b'\0'
        strings.append({'pointer_offset':off,'runtime_address':address,'earlier_image_target_offset':target,'string':value.decode()})
    printer=code(0x4530,0x4536);assert printer[0x4530][:2]==('lrw','r0, 0x10008114') and printer[0x4532][:2]==('bsr','0x61f4')
    jump=code(0x4aa6,0x4aae)
    assert jump[0x4aa6][:2]==('lrw','r2, 0x1000812c')
    assert jump[0x4aa8][:2]==('ldr.w','r3, (r2, r3 << 2)') and jump[0x4aac][:2]==('jmp','r3')
    table=stock[0x817c:0x817c+18*4];targets=[int.from_bytes(table[i:i+4],'little') for i in range(0,len(table),4)]
    assert all(0x10004a48<=target<0x10004c00 and target%2==0 for target in targets)
    return {'census':census,'strings':strings,'jump_table':{'pointer_offset':0x4ab0,'runtime_address':0x1000812c,'earlier_image_offset':0x817c,'entries':targets,'bytes_sha256':sha(table),'indexed_load_pc':0x4aa8,'indirect_jump_pc':0x4aac},'cross_image_lifetime_resolved':False,'limits':['All five stored addresses identify earlier-image strings or a used jump table under its package+0x10000000-0x50 mapping. They are real data references, not arbitrary patterns. This classification alone does not prove those consumers cannot execute after the backup image occupies the same addresses. Source LDO integration remains pending lifetime qualification.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-ldo-references.json').write_text(json.dumps(r,indent=2)+'\n');print('Five earlier-image LDO address aliases identified')

# SPDX-License-Identifier: MIT
"""Build shared recovered SPI registry initialization and state for backup firmware."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def build():
    out=ROOT/'build/gx8002-backup-device-list'; out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_device_list_init.c'
    text=source.read_text()+'\nvolatile struct open_cfw_device_list open_cfw_gx8002_device_heads[2];\n'
    (out/'device.c').write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-common','-c',str(out/'device.c'),'-o',str(out/'device.o')]
    subprocess.run(command,check=True)
    script='''SECTIONS {
.device_list_init 0x10008204 : { *(.text.open_cfw_gx8002_device_list_init) }
.device_heads 0x20017660 (NOLOAD) : { *(.bss.open_cfw_gx8002_device_heads) }
}
device_list_init = open_cfw_gx8002_device_list_init;
ASSERT(SIZEOF(.device_list_init) <= 20, "device initializer overflow")
ASSERT(SIZEOF(.device_heads) == 16, "device heads ABI")
'''
    (out/'device.ld').write_text(script)
    path=out/'device.elf';subprocess.run([pre+'ld','-T',str(out/'device.ld'),str(out/'device.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'device');sec=next(s for s in elf.sections if s['name']=='.device_list_init');body=elf.contents(sec)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert body==stock[0x40b44:0x40b58]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    state=next(s for s in elf.sections if s['name']=='.device_heads')
    assert state['type']==8 and 0x20017090<=state['address'] and state['address']+state['size']<=0x2002d79c
    asm=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'device.disassembly.txt').write_text(asm)
    code=decode(asm);pc=0x10008204
    sequence=[('lrw','r3, 0x20017660',2),('addi','r2, r3, 8',2),('st.w','r3, (r3, 0x0)',2),('st.w','r3, (r3, 0x4)',2),('st.w','r2, (r3, 0x8)',2),('st.w','r2, (r3, 0xc)',2),('rts','',2)]
    for instruction in sequence:
        assert code[pc]==instruction;pc+=instruction[2]
    report={'source_sha256':sha(source.read_bytes()),'derived_source_sha256':sha(text.encode()),'command':command,'elf_sha256':sha(path.read_bytes()),'stock_byte_exact':True,'compiled_bytes':len(body),'state_bytes':16,'ordered_writes':[[0x20017660,0x20017660],[0x20017664,0x20017660],[0x20017668,0x20017668],[0x2001766c,0x20017668]],'source_admitted':False,'hardware_qualified':False,'limits':['Shared recovered C creates two empty circular lists. Exact stock bytes and the straight-line decoded store sequence establish this component behavior; downstream registry operations and full firmware remain incomplete.']}
    (ROOT/'docs/research/gx8002-backup-device-list.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(json.dumps(build(),indent=2))

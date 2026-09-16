# SPDX-License-Identifier: MIT
"""Compile named backup flash table and state; stock only verifies output."""
import json, subprocess, struct
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
CALLBACKS={'flash_interface_initialize':0x10007d78,'flash_read':0x10006e64,
'flash_chip_erase':0x10007f78,'flash_erase':0x1000764c,'flash_page_program':0x100074c0,
'flash_sync':0x10007118,'flash_block_range':0x100075d0,'flash_gettype':0x10007f58,
'flash_getinfo':0x10006eb8,'flash_write_protect_mode':0x10006fc8,
'flash_write_protect_status':0x10006fac,'flash_write_protect_lock':0x100070f8,
'flash_write_protect_unlock':0x10007108,'flash_otp_lock':0x1000715c,
'flash_otp_status':0x100071d4,'flash_otp_erase':0x1000723c,
'flash_otp_write':0x10007884,'flash_otp_read':0x100079e8,
'flash_otp_get_region':0x100072e8,'flash_otp_set_region':0x100072fc,
'flash_otp_get_current_region':0x10007324,'flash_otp_get_region_size':0x1000733c}

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-flash-storage';out.mkdir(parents=True,exist_ok=True)
    base=ROOT/'components/shared/gx8002';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    sources={'table':'runtime_gx8002_backup_flash_interface_table.c','state':'runtime_gx8002_flash_state.c'}
    for name,filename in sources.items():subprocess.run([pre+'gcc',*FLAGS,'-c',str(base/filename),'-o',str(out/(name+'.o'))],check=True)
    script='SECTIONS { .flash_state 0x20016d60 : { *(.data.open_cfw_gx8002_flash_state) }\n.flash_interface_table 0x20016d80 : { *(.data.open_cfw_gx8002_flash_interface) } }\n'
    script+=''.join(f'open_cfw_gx8002_{k} = {v:#x};\n' for k,v in CALLBACKS.items())
    (out/'storage.ld').write_text(script);path=out/'storage.elf'
    subprocess.run([pre+'ld','-T',str(out/'storage.ld'),str(out/'table.o'),str(out/'state.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'flash storage');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    sections=[]
    for name,address,offset,size in (('.flash_state',0x20016d60,0x4f6a0,32),('.flash_interface_table',0x20016d80,0x4f6c0,120)):
        sec=next(s for s in elf.sections if s['name']==name);payload=elf.contents(sec)
        assert sec['address']==address and sec['size']==size and sec['align']==4 and sec['flags']==3 and not elf.relocations(sec['index'])
        assert payload==stock[offset:offset+size]
        if name=='.flash_state':assert payload==struct.pack('<8I',0xffffffff,0,0,0,0,0,0,0)
        else:assert struct.unpack_from('<I',payload,116)[0]==0 and sum(bool(v) for v in struct.unpack('<30I',payload))==22
        sections.append({'section':name,'address':address,'package_offset':offset,'bytes':size,'sha256':sha(payload),'byte_exact':True})
    report={'source_sha256':{n:sha((base/f).read_bytes()) for n,f in sources.items()},'headers_sha256':{n:sha((base/n).read_bytes()) for n in ('runtime_gx8002_flash_state.h','runtime_gx8002_flash_interface_table.h')},'flags':FLAGS,'callbacks':CALLBACKS,'sections':sections,'source_admitted':False,'hardware_qualified':False,'limits':['Named source initial state and dispatch pointers, not binary payload arrays. Callback addresses in this standalone link remain external dependencies; behavior qualification and full source closure are separate.']}
    (ROOT/'docs/research/gx8002-backup-flash-storage.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))

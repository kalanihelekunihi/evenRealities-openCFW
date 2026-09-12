# SPDX-License-Identifier: MIT
"""Check recovered receive-buffer C independently of its stock placement."""
import json,subprocess
from itertools import product
from verify_gx8002_uart_receive_buffer import verify as baseline,execute,ROOT,decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha,IMAGE
from analyze_g2_codec_fwpk_segments import parse_fwpk,parse_main_image,FLASH_XIP_BASE


def verify():
    dependency=baseline();out=ROOT/'build/gx8002-uart-receive-buffer-relocated';out.mkdir(parents=True,exist_ok=True)
    entry=0x10350000
    stock=IMAGE.read_bytes();records=parse_fwpk(stock)["records"]
    main=parse_main_image(stock[records[1]["offset"]:])["image_a"]
    xip_start=FLASH_XIP_BASE+main["stage2_offset"]
    xip_end=xip_start+main["stage2_xip_text_size"]
    script=out/'buffer.ld';script.write_text(f'SECTIONS {{ .text {entry:#x} : {{ *(.text.open_cfw_gx8002_uart_receive_buffer) }} /DISCARD/ : {{ *(.text*) }} }}\nopen_cfw_gx8002_uart_descriptors = 0x20026a94;\nopen_cfw_gx8002_uart_receive_dma = 0x10203190;\nopen_cfw_gx8002_irq_save = 0x10025560;\nopen_cfw_gx8002_irq_restore = 0x1002556c;\n')
    prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');target=out/'buffer.elf'
    subprocess.run([prefix+'ld','-T',str(script),str(ROOT/'build/gx8002-uart-receive-buffer/control.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));section=next(s for s in elf.sections if s['name']=='.text')
    if elf.relocations(section['index']) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Relocated link unresolved')
    text=subprocess.check_output([prefix+'objdump','-d',str(target)],text=True);(out/'buffer.disassembly.txt').write_text(text)
    code=decode(text);original=decode((ROOT/'build/gx8002-uart-receive-buffer/buffer.disassembly.txt').read_text());cases=0
    for args in product((0,1),(0,0x20050000),(0,1,32,0xffffffff),(0,0x10207ee0),(0,0x12345678),(0,1,0xffffffff),(0,0x40,0xffffffff),(0,1),(0,0xffffffff)):
        if execute(code,entry,*args)!=execute(original,0x10203780,*args):raise ValueError('Relocated behavior changed')
        cases+=1
    return {'dependency':dependency,'entry':entry,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),
        'decoded_cases':cases,'current_xip_range':[xip_start,xip_end],
        'fits_current_xip_mapping':xip_start<=entry and entry+section['size']<=xip_end,'source_admitted':False,'hardware_qualified':False,
        'limits':['Analysis-only link address, not assigned firmware space. Entry redirection and physical placement remain unresolved; helper behavior modeled.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-receive-buffer-relocated.json').write_text(json.dumps(r,indent=2)+'\n');print(r['compiled_bytes'],r['decoded_cases'])

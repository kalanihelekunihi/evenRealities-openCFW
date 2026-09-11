# SPDX-License-Identifier: MIT
"""RTC diagnostic string through decoded stock/source formatters."""
import json
import subprocess
from build_transparent_image import Elf32
from compare_gx8002_format import execute,decode,ROOT


def verify():
    elf=Elf32((ROOT/'build/gx8002-board/rtc-error.o').read_bytes(),'RTC diagnostic')
    sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    if len(sections)!=1:raise ValueError('RTC diagnostic sections')
    text=elf.contents(sections[0])
    if text!=b'RTC prescaler error!\n\0':raise ValueError('RTC diagnostic content')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');out=ROOT/'build/gx8002-tinyprintf'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x10010','--stop-address=0x101b0',str(out/'stock.elf')],text=True))
    new=decode(subprocess.check_output([pre,'-d','--section=.text.tfp_format',str(out/'formatter.elf')],text=True))
    targets={0xfeac:'integer',0xff24:'character',0xff3c:'padding'}
    results=[]
    for code,start,helpers in ((old,0x10010,targets),(new,0x10206a84,{a+0x101f6a74:k for a,k in targets.items()})):
        result,output=execute(code,start,helpers,text[:-1],[])
        if output!=text[:-1]:raise ValueError('RTC formatter bytes')
        results.append(result)
    if results[0]!=results[1]:raise ValueError('RTC formatter return')
    return {'decoded_cases':2,'output_text':text[:-1].decode(),'formatter_result':results[0],'source_admitted':False,
            'limits':['Decoded formatting with modeled character output; printf wrapper and physical UART not composed here. Existing registered artifacts read only.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-rtc-diagnostic-format.json').write_text(json.dumps(report,indent=2)+'\n');print('RTC diagnostic formatting passed')

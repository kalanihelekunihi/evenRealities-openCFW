# SPDX-License-Identifier: MIT
"""Board pin setup diagnostic string through decoded stock/source formatters."""
import json
import subprocess
from build_transparent_image import Elf32
from verify_gx8002_console_boundary import execute as console, programs as console_programs
from compare_gx8002_uart_putc import execute as uart
from compare_gx8002_uart_transmit import execute as transmit
from execute_gx8002_format_composed import execute,decode,ROOT
from compare_gx8002_ui2a import execute as integer
from execute_gx8002_padding_composed import execute as padding
from verify_gx8002_fputc_boundary import execute as fputc, programs as fputc_programs
from verify_gx8002_putf_boundary import execute as putf, programs as putf_programs


def verify():
    elf=Elf32((ROOT/'build/gx8002-board/board-pin-setup-error.o').read_bytes(),'Board pin setup diagnostic')
    sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    if len(sections)!=1:raise ValueError('Board pin setup diagnostic sections')
    text=elf.contents(sections[0])
    if text!=b'!!!pin set error!\n Please check Board Options!!!\0':raise ValueError('Board pin setup diagnostic content')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');out=ROOT/'build/gx8002-tinyprintf'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x10010','--stop-address=0x101b0',str(out/'stock.elf')],text=True))
    new=decode(subprocess.check_output([pre,'-d','--section=.text.tfp_format',str(out/'formatter.elf')],text=True))
    old_integer=decode(subprocess.check_output([pre,'-D','--start-address=0xfeac','--stop-address=0xff24',str(out/'stock.elf')],text=True))
    new_integer=decode(subprocess.check_output([pre,'-d','--section=.text.ui2a',str(out/'formatter.elf')],text=True))
    old_padding=decode(subprocess.check_output([pre,'-D','--start-address=0xff3c','--stop-address=0x10010',str(out/'stock.elf')],text=True))
    new_padding=decode(subprocess.check_output([pre,'-d','--section=.text.putchw',str(out/'formatter.elf')],text=True))
    uart_out=ROOT/'build/gx8002-uart-console'
    old_tx=decode(subprocess.check_output([pre,'-D','--start-address=0xc7d8','--stop-address=0xc7ec',str(uart_out/'stock.elf')],text=True))
    new_tx=decode(subprocess.check_output([pre,'-d','--section=.text.open_cfw_gx8002_uart_transmit',str(uart_out/'console.elf')],text=True))
    putfs=putf_programs()
    fputcs=fputc_programs()
    consoles,uarts=console_programs()
    targets={0xfeac:'integer',0xff24:'character',0xff3c:'padding'}
    count=0
    for pin in (0,):
        signed=pin if pin<0x80000000 else pin-0x100000000
        want=text[:-1]
        results=[]
        for code,start,helpers in ((old,0x10010,targets),(new,0x10206a84,{a+0x101f6a74:k for a,k in targets.items()})):
            for leaf,leaf_start in ((old_integer,0xfeac),):
                def hook(number,base,upper):
                    raise ValueError('Unexpected integer conversion in literal diagnostic')
                for pad,pad_start,target in ((old_padding,0xff3c,0xff24),):
                    for ch,ch_start,ch_target in ((putfs[0],0xff24,0x101fc),(putfs[1],0x10206998,0x10206c70)):
                        emitted=[];transmitted=[]
                        def character_hook(character,success):
                            def fputc_hook(value,stream):
                                source=ch_start==0x10206998
                                def console_hook(value):
                                    def uart_hook(port,char):
                                        transmitted.extend(uart(uarts[int(source)],0x102035b4 if source else 0xcb40,0x1020324c if source else 0xc7d8,port,char))
                                    trace=console(consoles[int(source)],0x102037f0 if source else 0xcd7c,0x102035b4 if source else 0xcb40,value,0,uart_hook)
                                    if trace!=[('read',0x2002731c,0),('uart',0,value)]:raise ValueError('Diagnostic console trace')
                                result,calls=fputc(fputcs[int(source)],0x10206c70 if source else 0x101fc,0x102037f0 if source else 0xcd7c,value,stream,0xffffffff,console_hook=console_hook)
                                if calls!=[character]:raise ValueError('Diagnostic console forwarding')
                                return result
                            result,calls=putf(ch,ch_start,ch_target,0x3000,character,0xffffffff,fputc_hook=fputc_hook)
                            if calls!=[(character,0x3000)]:raise ValueError('Diagnostic character forwarding')
                            emitted.append(character)
                            return result
                        def pad_hook(*args):raise ValueError('Unexpected padding in literal diagnostic')
                        result,output=execute(code,start,helpers,text[:-1],[],integer_hook=hook,padding_hook=pad_hook,character_hook=character_hook)
                        if output!=want or bytes(emitted)!=want:raise ValueError('Board pin formatter bytes')
                        expected_transmit=[(0x20026a94,value) for value in want.replace(b'\n',b'\r\n')]
                        if transmitted!=expected_transmit:raise ValueError('Diagnostic UART transmit sequence')
                        for descriptor,value in transmitted:
                            for tx,tx_start in ((old_tx,0xc7d8),(new_tx,0x1020324c)):
                                observed=transmit(tx,tx_start,descriptor,0xa0000000,value,[0,32])
                                want_tx=('returned',[('read',descriptor+4,4,0xa0000000),('read',0xa0000014,4,0),('read',0xa0000014,4,32),('write',0xa0000000,4,value)])
                                if observed!=want_tx:raise ValueError('Diagnostic transmitter MMIO')
                        results.append(result)
                        count+=1
        if len(set(results))!=1:raise ValueError('Board pin formatter return')
    return {'decoded_cases':count,'source_admitted':False,
            'limits':['Decoded literal formatter/putf composition (integer and padding calls rejected) with separate helper memory and translated buffers. Matched stock/source fputc, console and UART wrappers decoded at selected port zero. Each transmit call checked against both decoded transmitter bodies with scripted busy/ready MMIO. Physical UART remains unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-board-pin-setup-diagnostic-format.json').write_text(json.dumps(report,indent=2)+'\n');print('Board pin setup diagnostic formatting passed')

# SPDX-License-Identifier: MIT
"""Build the authenticated upstream UART receive registration on macOS."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def extract(source, signature):
    start=source.index(signature+'\n{'); opening=source.index('{',start); depth=1; end=opening+1
    while depth:
        depth += (source[end]=='{')-(source[end]=='}'); end+=1
    return source[start:end]+'\n'


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'; rel='lvp/common/uart_message_v2.c'
    raw=subprocess.check_output(['git','-C',str(sdk),'show',SDK_COMMIT+':'+rel])
    if raw!=(sdk/rel).read_bytes():raise ValueError('Upstream source identity')
    headers={}
    for name in ('uart_message_v2.h','lvp_queue.h'):
        path='lvp/common/'+name; content=(sdk/path).read_bytes()
        if content!=subprocess.check_output(['git','-C',str(sdk),'show',SDK_COMMIT+':'+path]):raise ValueError('Header identity')
        headers[name]=sha(content)
    source=raw.decode()
    declarations=source[source.index('typedef enum {'):source.index('#ifdef CONFIG_UART_MESSAGE_PORT_BOTH')]
    function=extract(source,'int UartMessageAsyncDone(void)')
    function=function.replace('while (port_index < 2) {','#pragma GCC unroll 1\n    do {').replace('    }\n\n    memset','    } while (port_index < 2);\n\n    memset',1)
    function=function.replace('port_index ++;', 'port_index ++;\n        __asm__ volatile ("" : "+r" (port_index));')
    text=source[:source.index('#include')]+'\n#include <stddef.h>\n#include "uart_message_v2.h"\n#include "lvp_queue.h"\n#define UART_SEND_QUENE_LEN 8\n'+declarations+'\nextern MESSAGE_HANDLE *_GetMessageHandle(unsigned char);\nextern int gx_uart_async_send_buffer_stop(unsigned);\nextern int gx_uart_async_recv_buffer_stop(unsigned);\nextern void *memset(void *,int,unsigned);\nextern UART_MSG_REGIST s_uart_msg_regist_array[16];\nextern LVP_QUEUE s_uart_recv_pack_queue;\nextern MESSAGE_HANDLE s_msg_handle[2];\n_Static_assert(sizeof(MESSAGE_HANDLE)==380,"context ABI");\n_Static_assert(sizeof(UART_MSG_REGIST)==28,"registration ABI");\n'+function
    out=ROOT/'build/gx8002-uart-message-done';out.mkdir(parents=True,exist_ok=True)
    path=out/'callback.c';path.write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags=['-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-fno-peel-loops','-fno-tree-ch','-Wno-error=sign-compare','-Wno-error=unused-parameter','-Wno-error=address-of-packed-member','-I'+str(sdk/'lvp/common')]
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'callback.o')],check=True)
    bindings={'_GetMessageHandle':0x10207ac0,'gx_uart_async_send_buffer_stop':0x102036e8,'gx_uart_async_recv_buffer_stop':0x10203704,'memset':0x102099cc,'s_uart_msg_regist_array':0x2002e360,'s_uart_recv_pack_queue':0x2002ecc4,'s_msg_handle':0x2002e050}
    script='SECTIONS { .text 0x1020854c : { *(.text*) } }\n'+''.join('%s = %#x;\n'%item for item in bindings.items())
    (out/'callback.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'callback.ld'),str(out/'callback.o'),'-o',str(out/'callback.elf')],check=True)
    elf=Elf32((out/'callback.elf').read_bytes(),'callback')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name']!='.text' for s in elf.sections):raise ValueError('Unexpected allocation')
    payload=elf.contents(next(s for s in elf.sections if s['name']=='.text'));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    (out/'callback.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'callback.elf')],text=True))
    return {'sdk_commit':SDK_COMMIT,'upstream_sha256':sha(raw),'headers_sha256':headers,'generated_source_sha256':sha(path.read_bytes()),'flags':flags,'bindings':bindings,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':88,'stock_sha256':sha(stock[0x11ad8:0x11b30]),'fits':len(payload)<=88,'exact_stock':payload==stock[0x11ad8:0x11b30],'source_admitted':False,'hardware_qualified':False,'limits':['Source-built candidate only; complete decoded state-machine comparison and admission remain pending. External state uses established RAM addresses.']}


if __name__=='__main__':
    result=build();(ROOT/'docs/research/gx8002-uart-message-done-candidate.json').write_text(json.dumps(result,indent=2)+'\n');print(result)

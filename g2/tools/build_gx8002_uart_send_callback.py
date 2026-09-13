# SPDX-License-Identifier: MIT
"""Build the authenticated upstream UART transmit state machine on macOS."""
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
    source=raw.decode(); declarations=source[source.index('typedef enum {'):source.index('#ifdef CONFIG_UART_MESSAGE_PORT_BOTH')]
    check=extract(source,'static int _UartMessageAsyncSendCheckCallback(MSG_PACK *pack, void *priv)')
    header=extract(source,'static int _UartMessageAsyncSendHeader(int port, MESSAGE_HEADER *msg_header, unsigned int *send_len)')
    crc=extract(source,'static int _UartMessageAsyncSendCrC(int port, MSG_PACK* pack, unsigned int *send_len)')
    callback=extract(source,'static int _UartMessageAsyncSendCallback(int port, int length, void *priv)')
    header=header.replace('static unsigned int send_count[2] = {0, 0};','').replace('send_count','header_count')
    crc=crc.replace('static unsigned int send_count[2] = {0};','').replace('static unsigned int crc[2] = {0};','').replace('send_count','crc_count')
    callback=callback.replace('static int _UartMessageAsyncSendCallback','int open_cfw_gx8002_uart_send_callback',1)
    text=source[:source.index('#include')]+'\n#include <stddef.h>\n#include "uart_message_v2.h"\n#include "lvp_queue.h"\n#define UART_SEND_QUENE_LEN 8\n#define UART_MSG_SEND_CALLBACK_NUM 6\n#define MESSAGE_BODY_VEF_LEN 4\n'+declarations+'\ntypedef struct { unsigned port; UART_MSG_ID msg_id; MSG_PACK_CALLBACK msg_pack_callback; void *priv; } UART_MSG_SEND_CALLBACK;\nextern UART_MSG_SEND_CALLBACK s_send_callback[6];\nextern unsigned uart_state[];\n#define header_count (uart_state + 324)\n#define crc_count (uart_state + 326)\n#define crc (uart_state + 328)\n_Static_assert(sizeof(MESSAGE_HEADER)==14,"header ABI");\n_Static_assert(sizeof(MESSAGE_HANDLE)==380,"context ABI");\n_Static_assert(offsetof(MESSAGE_HANDLE,cur_send_pack)==60,"send packet ABI");\n_Static_assert(offsetof(MESSAGE_HANDLE,send_state)==372,"state ABI");\n_Static_assert(sizeof(UART_MSG_SEND_CALLBACK)==16,"completion table ABI");\nextern MESSAGE_HANDLE *_GetMessageHandle(unsigned char);\nextern int LvpPmuSuspendUnlock(int);\nextern int _UartMessageSendCheck(unsigned char);\nextern int _UartMessageAsyncSendBody(int,MSG_PACK *,unsigned *);\nextern int gx_uart_write(int,const unsigned char *,unsigned);\nextern unsigned crc32(unsigned,const void *,unsigned);\n'+check+header+crc+callback
    out=ROOT/'build/gx8002-uart-send-callback';out.mkdir(parents=True,exist_ok=True)
    path=out/'callback.c';path.write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags=['-Os',*FLAGS[1:],'-Wno-error=sign-compare','-Wno-error=unused-parameter','-I'+str(sdk/'lvp/common')]
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'callback.o')],check=True)
    bindings={'uart_state':0x2002e050,'_GetMessageHandle':0x10207ac0,'LvpPmuSuspendUnlock':0x102077d4,'_UartMessageSendCheck':0x10207adc,'_UartMessageAsyncSendBody':0x10207b38,'gx_uart_write':0x10203604,'crc32':0x102098a8,'s_send_callback':0x2002e578,'header_count':0x2002e560,'crc_count':0x2002e568,'crc':0x2002e570}
    script='SECTIONS { .text 0x10207f08 : { *(.text*) } }\n'+''.join('%s = %#x;\n'%item for item in bindings.items())
    (out/'callback.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'callback.ld'),str(out/'callback.o'),'-o',str(out/'callback.elf')],check=True)
    elf=Elf32((out/'callback.elf').read_bytes(),'callback')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name']!='.text' for s in elf.sections):raise ValueError('Unexpected allocation')
    payload=elf.contents(next(s for s in elf.sections if s['name']=='.text'));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    (out/'callback.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'callback.elf')],text=True))
    return {'sdk_commit':SDK_COMMIT,'upstream_sha256':sha(raw),'headers_sha256':headers,'generated_source_sha256':sha(path.read_bytes()),'flags':flags,'bindings':bindings,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':400,'stock_sha256':sha(stock[0x11494:0x11624]),'fits':len(payload)<=400,'exact_stock':payload==stock[0x11494:0x11624],'source_admitted':False,'hardware_qualified':False,'limits':['Source-built candidate only; complete decoded state-machine comparison and admission remain pending. External state uses established RAM addresses.']}


if __name__=='__main__':
    result=build();(ROOT/'docs/research/gx8002-uart-send-callback-candidate.json').write_text(json.dumps(result,indent=2)+'\n');print(result)

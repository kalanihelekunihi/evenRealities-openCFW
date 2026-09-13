# SPDX-License-Identifier: MIT
"""Build the authenticated upstream UART receive state machine on macOS."""
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
    check=extract(source,'static int _CheckCrc(unsigned char *data, int len, unsigned int crc_stand)')
    magic=extract(source,'static int _UartMessageAsyncRecvFindMagic(unsigned int magic, unsigned int *tmp_magic, unsigned char **recv_buffer_p, unsigned int *buffer_len)')
    header=extract(source,'static int _UartMessageAsyncRecvCheckHeader(unsigned int port, MESSAGE_HEADER *msg_header, unsigned char **recv_buffer_p, unsigned int *buffer_len)')
    verification=extract(source,'static int _UartMessageAsyncRecvBodyVerification(unsigned int port, unsigned int *tmp_vef, MSG_PACK* pack, unsigned char **recv_buffer_p, unsigned int *buffer_len)')
    callback=extract(source,'static int _UartMessageAsyncRecvCallback(int port, int length, void* priv)')
    header=header.replace('static unsigned int s_recv_header_data_count[2] = {4, 4};','')
    verification=verification.replace('static unsigned int vef_recv_count[2] = {0};','')
    callback=callback.replace('static unsigned char *recv_buffer;','').replace('static int _UartMessageAsyncRecvCallback','int open_cfw_gx8002_uart_receive_callback',1)
    callback=callback.replace('recv_buffer','receive_pointer').replace('s_uart_receive_pointer','s_uart_recv_buffer')
    text=source[:source.index('#include')]+'\n#include <stddef.h>\n#include "uart_message_v2.h"\n#include "lvp_queue.h"\n#define UART_SEND_QUENE_LEN 8\n'+declarations+'\nstruct receive_ram_layout {\n    unsigned char preceding[1416];\n    unsigned char *buffer_pointer;\n    unsigned verification_count[2];\n};\nextern struct receive_ram_layout receive_ram;\n#define s_uart_recv_buffer (receive_ram.preceding+1232)\n#define receive_pointer (receive_ram.buffer_pointer)\n#define vef_recv_count (receive_ram.verification_count)\nextern unsigned s_recv_header_data_count[2];\nextern MESSAGE_HANDLE *_GetMessageHandle(unsigned char);\nextern int gx_uart_read(int,unsigned char *,unsigned);\nextern unsigned crc32(unsigned,const void *,unsigned);\nextern int _UartMessageAsyncRecvCheckBody(unsigned,MSG_PACK *,unsigned char **,unsigned *);\nextern LVP_QUEUE s_uart_recv_pack_queue;\n_Static_assert(sizeof(MESSAGE_HEADER)==14,"header ABI");\n_Static_assert(sizeof(MESSAGE_HANDLE)==380,"context ABI");\n_Static_assert(offsetof(MESSAGE_HANDLE,cur_recv_pack)==28,"packet ABI");\n_Static_assert(offsetof(MESSAGE_HANDLE,recv_state)==368,"state ABI");\n_Static_assert(offsetof(struct receive_ram_layout,buffer_pointer)==1416,"buffer pointer ABI");\n'+check+magic+header+verification+callback
    out=ROOT/'build/gx8002-uart-receive-callback';out.mkdir(parents=True,exist_ok=True)
    path=out/'callback.c';path.write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags=['-Os',*FLAGS[1:],'-fno-guess-branch-probability','-Wno-error=sign-compare','-Wno-error=unused-parameter','-Wno-error=address-of-packed-member','-I'+str(sdk/'lvp/common')]
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'callback.o')],check=True)
    bindings={'receive_ram':0x2002e050,'_GetMessageHandle':0x10207ac0,'gx_uart_read':0x102035d8,'crc32':0x102098a8,'_UartMessageAsyncRecvCheckBody':0x10207cec,'s_recv_header_data_count':0x20026c74,'s_uart_recv_pack_queue':0x2002ecc4,'LvpQueuePut':0x100261b8}
    script='SECTIONS { .text 0x10208098 : { *(.text*) } }\n'+''.join('%s = %#x;\n'%item for item in bindings.items())
    (out/'callback.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'callback.ld'),str(out/'callback.o'),'-o',str(out/'callback.elf')],check=True)
    elf=Elf32((out/'callback.elf').read_bytes(),'callback')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name']!='.text' for s in elf.sections):raise ValueError('Unexpected allocation')
    payload=elf.contents(next(s for s in elf.sections if s['name']=='.text'));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    (out/'callback.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'callback.elf')],text=True))
    return {'sdk_commit':SDK_COMMIT,'upstream_sha256':sha(raw),'headers_sha256':headers,'generated_source_sha256':sha(path.read_bytes()),'flags':flags,'bindings':bindings,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':532,'stock_sha256':sha(stock[0x11624:0x11838]),'fits':len(payload)<=532,'exact_stock':payload==stock[0x11624:0x11838],'source_admitted':False,'hardware_qualified':False,'limits':['Source-built candidate only; complete decoded state-machine comparison and admission remain pending. External state uses established RAM addresses.']}


if __name__=='__main__':
    result=build();(ROOT/'docs/research/gx8002-uart-receive-callback-candidate.json').write_text(json.dumps(result,indent=2)+'\n');print(result)

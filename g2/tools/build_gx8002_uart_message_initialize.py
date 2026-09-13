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
    function=extract(source,'int UartMessageAsyncInit(UART_MSG_INIT_CONFIG *config)')
    function=function.replace('MESSAGE_HANDLE *msg_handle = _GetMessageHandle(config->port);','unsigned int initial_port = config->port;\n    MESSAGE_HANDLE *msg_handle = _GetMessageHandle(initial_port);').replace('msg_handle->port = config->port;','msg_handle->port = initial_port;').replace('gx_uart_async_send_buffer_stop(msg_handle->port);','gx_uart_async_send_buffer_stop(initial_port);')
    function=function.replace('"UartMessageAsyncSuspend"','suspend_label').replace('"UartMessageAsyncResume"','resume_label')
    text=source[:source.index('#include')]+'\n#include <stddef.h>\n#include "uart_message_v2.h"\n#include "lvp_queue.h"\n#define UART_SEND_QUENE_LEN 8\n#define UART_RECV_QUENE_LEN 8\n'+declarations+'\nextern MESSAGE_HANDLE *_GetMessageHandle(unsigned char);\nextern int gx_uart_async_send_buffer_stop(unsigned);\nextern int gx_uart_async_recv_buffer_stop(unsigned);\nextern int gx_uart_init(unsigned,unsigned);\nextern int gx_uart_start_async_recv(unsigned,int (*)(int,int,void *),void *);\nextern int _UartMessageAsyncRecvCallback(int,int,void *);\nextern int UartMessageAsyncSuspend(void *),UartMessageAsyncResume(void *);\ntypedef struct { int (*suspend_callback)(void *); const void *priv; } LVP_SUSPEND_INFO;\ntypedef struct { int (*resume_callback)(void *); const void *priv; } LVP_RESUME_INFO;\nextern int LvpSuspendInfoRegist(LVP_SUSPEND_INFO *);\nextern int LvpResumeInfoRegist(LVP_RESUME_INFO *);\nextern int LvpPmuSuspendLockCreate(int *);\nextern LVP_QUEUE s_uart_recv_pack_queue;\nextern unsigned char s_uart_recv_pack_queue_buffer[256];\nconst char suspend_label[] __attribute__((section(".rodata.suspend_label"),aligned(1))) = "UartMessageAsyncSuspend";\nconst char resume_label[] __attribute__((section(".rodata.resume_label"),aligned(1))) = "UartMessageAsyncResume";\n_Static_assert(sizeof(MESSAGE_HANDLE)==380,"context ABI");\n_Static_assert(sizeof(LVP_SUSPEND_INFO)==8,"power callback ABI");\n'+function
    out=ROOT/'build/gx8002-uart-message-initialize';out.mkdir(parents=True,exist_ok=True)
    path=out/'callback.c';path.write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags=['-Os',*FLAGS[1:],'-Wno-error=sign-compare','-Wno-error=unused-parameter','-Wno-error=address-of-packed-member','-I'+str(sdk/'lvp/common')]
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'callback.o')],check=True)
    bindings={'_GetMessageHandle':0x10207ac0,'gx_uart_async_send_buffer_stop':0x102036e8,'gx_uart_async_recv_buffer_stop':0x10203704,'gx_uart_init':0x10203530,'gx_uart_start_async_recv':0x1020368c,'_UartMessageAsyncRecvCallback':0x10208098,'UartMessageAsyncSuspend':0x10207c74,'UartMessageAsyncResume':0x10207c9c,'LvpSuspendInfoRegist':0x102076c0,'LvpResumeInfoRegist':0x10207718,'LvpPmuSuspendLockCreate':0x10207770,'LvpQueueInit':0x10206f9c,'s_uart_recv_pack_queue':0x2002ecc4,'s_uart_recv_pack_queue_buffer':0x2002e5e4}
    script='SECTIONS { .text 0x10208458 : { *(.text*) } .rodata.suspend_label 0x1020b18b : { *(.rodata.suspend_label) } .rodata.resume_label 0x1020b1a3 : { *(.rodata.resume_label) } }\n'+''.join('%s = %#x;\n'%item for item in bindings.items())
    (out/'callback.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'callback.ld'),str(out/'callback.o'),'-o',str(out/'callback.elf')],check=True)
    elf=Elf32((out/'callback.elf').read_bytes(),'callback')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name'] not in ('.text','.rodata.suspend_label','.rodata.resume_label') for s in elf.sections):raise ValueError('Unexpected allocation')
    payload=elf.contents(next(s for s in elf.sections if s['name']=='.text'));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    (out/'callback.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'callback.elf')],text=True))
    labels=[]
    for name in ('suspend_label','resume_label'):
        section=next(s for s in elf.sections if s['name']=='.rodata.'+name);data=elf.contents(section);offset=section['address']-0x101f6a74
        if data!=stock[offset:offset+len(data)]:raise ValueError('Source label identity')
        labels.append({'symbol':name,'section_name':section['name'],'package_offset':offset,'bytes':len(data),'sha256':sha(data)})
    return {'labels':labels,'sdk_commit':SDK_COMMIT,'upstream_sha256':sha(raw),'headers_sha256':headers,'generated_source_sha256':sha(path.read_bytes()),'flags':flags,'bindings':bindings,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':244,'stock_sha256':sha(stock[0x119e4:0x11ad8]),'fits':len(payload)<=244,'exact_stock':payload==stock[0x119e4:0x11ad8],'source_admitted':False,'hardware_qualified':False,'limits':['Source-built candidate only; complete decoded state-machine comparison and admission remain pending. External state uses established RAM addresses.']}


if __name__=='__main__':
    result=build();(ROOT/'docs/research/gx8002-uart-message-initialize-candidate.json').write_text(json.dumps(result,indent=2)+'\n');print(result)

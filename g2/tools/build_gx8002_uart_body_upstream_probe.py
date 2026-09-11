# SPDX-License-Identifier: MIT
"""Compile the authenticated upstream body-receive helper for analysis."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/common/uart_message_v2.c'
    data=subprocess.check_output(['git','-C',str(sdk),'show',SDK_COMMIT+':'+rel])
    if data!=(sdk/rel).read_bytes():raise ValueError('UART upstream source changed')
    headers={}
    for name in ('lvp/common/uart_message_v2.h','lvp/common/lvp_queue.h','include/driver/gx_uart.h'):
        raw=(sdk/name).read_bytes()
        if raw!=subprocess.check_output(['git','-C',str(sdk),'show',SDK_COMMIT+':'+name]):raise ValueError('Upstream header changed: '+name)
        headers[name]=sha(raw)
    source=data.decode();start=source.index('static int _UartMessageAsyncRecvCheckBody(unsigned int port, MSG_PACK* pack, unsigned char **recv_buffer_p, unsigned int *buffer_len)\n{')
    end=source.index('\nstatic int _UartMessageAsyncRecvBodyVerification(',start)
    prepare_start=source.index('static int _UartMessagePrepareRecv(MSG_PACK* pack)\n{')
    prepare_end=source.index('\nstatic int _uartRecvBufferCallback',prepare_start)
    preparation=source[prepare_start:prepare_end]
    helper=source[start:end].replace('static int _UartMessageAsyncRecvCheckBody','int open_cfw_gx8002_uart_body_probe',1)
    declarations=source[source.index('typedef enum {'):source.index('#ifdef CONFIG_UART_MESSAGE_PORT_BOTH')]
    out=ROOT/'build/gx8002-uart-body-probe';out.mkdir(parents=True,exist_ok=True)
    (out/'prepare.c').write_text(source[:source.index('#include')]+ '#include <stddef.h>\n#include "uart_message_v2.h"\nextern UART_MSG_REGIST s_uart_msg_regist_array[16];\n'+preparation)
    probe=out/'body.c';probe.write_text(source[:source.index('#include')]+'''
#include <stddef.h>
#include "uart_message_v2.h"
#include "lvp_queue.h"
#define UART_SEND_QUENE_LEN 8
'''+declarations+'''
extern MESSAGE_HANDLE *_GetMessageHandle(unsigned char);
extern UART_MSG_REGIST s_uart_msg_regist_array[16];
extern int _UartMessageAsyncRecvCallback(int,int,void *);
extern int _uartRecvBufferCallback(int,void *);
extern int gx_uart_start_async_recv(int,int (*)(int,int,void *),void *);
extern int gx_uart_stop_async_recv(int);
extern int gx_uart_async_recv_buffer(int,unsigned char *,int,int (*)(int,void *),void *);
extern LVP_QUEUE s_uart_recv_pack_queue;
extern unsigned char s_uart_recv_buffer[64];
'''+preparation+helper)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'body.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Wno-error=sign-compare','-I'+str(sdk/'lvp/common'),'-c',str(probe),'-o',str(obj)],check=True)
    prepare_target=out/'prepare-target.c'
    prepare_target.write_text((out/'prepare.c').read_text().replace('static int _UartMessagePrepareRecv','int open_cfw_gx8002_uart_prepare_probe',1))
    prepare_obj=out/'prepare-target.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Wno-error=sign-compare','-I'+str(sdk/'lvp/common'),'-c',str(prepare_target),'-o',str(prepare_obj)],check=True)
    prepare_script=out/'prepare-target.ld'
    prepare_script.write_text('SECTIONS { .text 0x10302000 : { *(.text*) } }\ns_uart_msg_regist_array = 0x2002e360;\n')
    prepare_elf=out/'prepare-target.elf'
    subprocess.run([pre+'ld','-T',str(prepare_script),str(prepare_obj),'-o',str(prepare_elf)],check=True)
    (out/'prepare-target.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(prepare_elf)],text=True))
    elf=Elf32(obj.read_bytes(),str(obj));sec=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_uart_body_probe')
    (out/'body.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-dr',str(obj)],text=True))
    bindings={'_GetMessageHandle':0x10207ac0,'gx_uart_start_async_recv':0x1020368c,
              'gx_uart_stop_async_recv':0x102036c0,'gx_uart_async_recv_buffer':0x10203780,
              'LvpQueuePut':0x100261b8,'_UartMessageAsyncRecvCallback':0x10208098,
              '_uartRecvBufferCallback':0x10207ee0,'s_uart_recv_buffer':0x2002e520,
              's_uart_recv_pack_queue':0x2002ecc4,'s_uart_msg_regist_array':0x2002e360}
    script=out/'body.ld'
    script.write_text('SECTIONS { .text 0x10301000 : { *(.text*) } .bss 0x2002e358 : { *(.bss*) } }\n'+
                      ''.join('%s = %#x;\n'%item for item in bindings.items()))
    linked=out/'body.elf'
    subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(linked)],check=True)
    target=Elf32(linked.read_bytes(),str(linked))
    if any(target.relocations(x['index']) for x in target.sections):raise ValueError('Body probe relocation')
    if any(x['name'] and x['section']==0 for x in target.symbols()):raise ValueError('Body probe unresolved symbol')
    (out/'body.linked.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(linked)],text=True))

    candidate_script=out/'body-candidate.ld'
    candidate_script.write_text(script.read_text().replace('0x10301000','0x10207cec'))
    candidate_elf=out/'body-candidate.elf'
    subprocess.run([pre+'ld','-T',str(candidate_script),str(obj),'-o',str(candidate_elf)],check=True)
    candidate=Elf32(candidate_elf.read_bytes(),str(candidate_elf))
    candidate_section=next(s for s in candidate.sections if s['name']=='.text')
    payload=candidate.contents(candidate_section)
    if len(payload)>500 or candidate.relocations(candidate_section['index']):raise ValueError('Body original-entry placement')
    (out/'body-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(candidate_elf)],text=True))
    return {'sdk_commit':SDK_COMMIT,'headers_sha256':headers,'upstream_sha256':sha(data),'probe_sha256':sha(probe.read_bytes()),'compiled_bytes':sec['size'],
            'candidate_address':0x10207cec,'candidate_bytes':len(payload),'candidate_sha256':sha(payload),'stock_envelope_bytes':500,'analysis_bindings':bindings,'analysis_address':0x10301000,'source_admitted':False,'hardware_qualified':False,
            'limits':['Linked analysis-only upstream body helper with analysis-only external declarations. Dependency ABI, stock equivalence, placement and whole-callback execution remain unqualified.']}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-uart-body-upstream-probe.json').write_text(json.dumps(r,indent=2)+'\n');print(r)

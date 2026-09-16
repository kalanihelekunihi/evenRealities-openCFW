# SPDX-License-Identifier: MIT
"""Pinned SDK UART receive dispatch candidate with original packet types."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-uart-async-tick';out.mkdir(exist_ok=True);records=[];text=''
    for rel in ('lvp/common/uart_message_v2.c','lvp/common/uart_message_v2.h','lvp/common/lvp_queue.h','base/src/crc32.c'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob)
        records.append({'path':rel,'blob':blob,'sha256':sha(data)})
        if rel=='lvp/common/uart_message_v2.c':text=data.decode()
        elif rel=='base/src/crc32.c':assert 'uint32_t crc32 (uint32_t crc, const unsigned char/*Bytef*/ *p, unsigned int/*uInt*/ len)' in data.decode()
        else:(out/rel.split('/')[-1]).write_bytes(data)
    def function(signature):
        start=text.index(signature);brace=text.index('{',start);end=brace+1;depth=1
        while depth:
            depth+=(text[end]=='{')-(text[end]=='}');end+=1
        return text[start:end]
    source='#include <stdint.h>\n#include <stddef.h>\n#include "uart_message_v2.h"\n#include "lvp_queue.h"\nextern LVP_QUEUE s_uart_recv_pack_queue;\nextern UART_MSG_REGIST s_uart_msg_regist_array[16];\nextern uint32_t crc32(uint32_t,const unsigned char*,unsigned int);\nextern int printf(const char*,...);\n_Static_assert(sizeof(MSG_PACK)==32,"packet size");\n_Static_assert(sizeof(UART_MSG_REGIST)==28,"registration stride");\n_Static_assert(offsetof(MSG_PACK,body_addr)==16,"body offset");\n_Static_assert(offsetof(MSG_PACK,port)==20,"port offset");\n'+function('static int _CheckCrc(')+'\n'+function('int UartMessageAsyncTick(void)')+'\n'
    (out/'tick.c').write_text(source);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-I',str(out),'-c',str(out/'tick.c'),'-o',str(out/'tick.o')];subprocess.run(command,check=True)
    script='SECTIONS { .async_tick 0x1000b4c8 : { *(.text*) } .async_message 0x10013624 : { *(.rodata*) } }\nLvpQueueGet = 0x10009fbc;\ns_uart_recv_pack_queue = 0x2002d770;\ns_uart_msg_regist_array = 0x2002cf30;\ncrc32 = 0x1000c5c4;\nprintf = 0x10009934;\nASSERT(SIZEOF(.async_tick) <= 132, "async overflow")\nASSERT(SIZEOF(.async_message) <= 16, "message overflow")\n'
    (out/'tick.ld').write_text(script);path=out/'tick.elf';subprocess.run([pre+'ld','-T',str(out/'tick.ld'),str(out/'tick.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'async tick');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    message=next(s for s in elf.sections if s['name']=='.async_message');assert elf.contents(message)==stock[0x4bf64:0x4bf64+message['size']]
    (out/'tick.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'sdk_commit':SDK_COMMIT,'upstream_files':records,'derived_source_sha256':sha(source.encode()),'command':command,'elf_sha256':sha(path.read_bytes()),'sections':[{'name':s['name'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']],'source_admitted':False,'limits':['Isolated SDK CRC-check and dispatch bodies, compiler-checked packet/registration geometry, source diagnostic matches stock.', 'Queue, CRC, printf and storage externally bound. CRC declaration authenticated from pinned SDK implementation; dispatch execution and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-uart-async-tick.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['sections'])

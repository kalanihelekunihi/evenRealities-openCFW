# SPDX-License-Identifier: MIT
"""Compile authenticated upstream declarations to measure the target ABI."""
import json
import struct
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS


def analyze():
    sdk = ROOT/'build/upstream-nationalchip-lvp-kws'
    evidence = {}
    for rel in ('lvp/common/uart_message_v2.c', 'lvp/common/uart_message_v2.h', 'lvp/common/lvp_queue.h'):
        data = (sdk/rel).read_bytes()
        original = subprocess.check_output(['git', '-C', str(sdk), 'show', SDK_COMMIT+':'+rel])
        if original != data: raise ValueError('Upstream layout source changed: '+rel)
        evidence[rel] = sha(data)
    source = (sdk/'lvp/common/uart_message_v2.c').read_text()
    declarations = source[source.index('typedef enum {'):source.index('#ifdef CONFIG_UART_MESSAGE_PORT_BOTH')]
    fields = ('magic', 'tmp_vef', 'port', 'init_flag', 'cur_recv_pack', 'cur_send_pack',
              'uart_send_pack_queue', 'recv_state', 'send_state', 'pmu_lock')
    registry_fields=('port','msg_id','msg_buffer','msg_buffer_length','msg_buffer_offset','msg_pack_callback','priv')
    out = ROOT/'build/gx8002-uart-message-layout'
    out.mkdir(parents=True, exist_ok=True)
    probe = out/'layout.c'
    probe.write_text('#include <stddef.h>\n#include "uart_message_v2.h"\n#include "lvp_queue.h"\n'
        '#define UART_SEND_QUENE_LEN 8\n'+declarations+
        '\nconst unsigned int layout[] = {sizeof(MESSAGE_HANDLE),sizeof(MSG_PACK),'+
        ','.join('offsetof(MESSAGE_HANDLE,'+field+')' for field in fields)+'};\n'+
        'const unsigned int registry_layout[] = {sizeof(UART_MSG_REGIST),'+
        ','.join('offsetof(UART_MSG_REGIST,'+field+')' for field in registry_fields)+'};\n')
    obj = out/'layout.o'
    subprocess.run([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-gcc'), *FLAGS,
                    '-I'+str(sdk/'lvp/common'), '-c', str(probe), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    sec = next(s for s in elf.sections if s['name']=='.rodata.layout')
    values = struct.unpack('<'+'I'*(2+len(fields)), elf.contents(sec))
    registry_sec=next(s for s in elf.sections if s['name']=='.rodata.registry_layout')
    registry=struct.unpack('<8I',elf.contents(registry_sec))
    if registry!=(28,0,4,8,12,16,20,24):raise ValueError('Registration ABI differs from stock field accesses')
    return {'registry_size':registry[0],'registry_offsets':dict(zip(registry_fields,registry[1:])), 'sdk_commit': SDK_COMMIT, 'sources_sha256': evidence, 'queue_length': 8,
            'message_handle_size': values[0], 'packet_size': values[1],
            'offsets': dict(zip(fields, values[2:])),
            'matches_stock_context_stride': values[0] == 0x17c,
            'source_admitted': False,
            'limits': ['ABI layout probe only, with queue length eight. No upstream callback equivalence or hardware execution claim.']}

if __name__ == '__main__':
    report = analyze()
    (ROOT/'docs/research/gx8002-uart-message-layout.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

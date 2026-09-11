# SPDX-License-Identifier: MIT
"""Compile the pinned upstream receive-header helper as an isolated probe."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    sdk = ROOT/'build/upstream-nationalchip-lvp-kws'
    rel = 'lvp/common/uart_message_v2.c'
    data = subprocess.check_output(['git', '-C', str(sdk), 'show', SDK_COMMIT+':'+rel])
    if data != (sdk/rel).read_bytes(): raise ValueError('Upstream UART source changed')
    source = data.decode()
    start = source.index('static int _UartMessageAsyncRecvCheckHeader(', source.index('static int _UartMessageAsyncRecvFindMagic(unsigned int magic, unsigned int *tmp_magic, unsigned char **recv_buffer_p, unsigned int *buffer_len)\n{'))
    end = source.index('\nstatic int _UartMessageAsyncRecvCheckBody(', start)
    helper = source[start:end].replace('static int _UartMessageAsyncRecvCheckHeader', 'int open_cfw_gx8002_uart_header_probe', 1)
    out = ROOT/'build/gx8002-uart-header-probe';out.mkdir(parents=True, exist_ok=True)
    c = out/'header.c'
    c.write_text(source[:source.index('#include')]+ '\n#include "uart_message_v2.h"\n'
        'extern unsigned int open_cfw_gx8002_crc32(unsigned int, const unsigned char *, unsigned int);\n'
        'static int _CheckCrc(unsigned char *data, int len, unsigned int expected) { return expected == open_cfw_gx8002_crc32(0, data, len); }\n'+helper)
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj = out/'header.o'
    subprocess.run([pre+'gcc', *FLAGS, '-Wno-error=sign-compare', '-I'+str(sdk/'lvp/common'), '-c', str(c), '-o', str(obj)], check=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_uart_header_probe')
    (out/'header.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-dr',str(obj)],text=True))
    # An isolated analysis address, not a claimed free firmware region.
    script = out/'header.ld'
    script.write_text('SECTIONS { .text 0x10300000 : { *(.text*) } .data 0x20026c74 : { *(.data*) } }\nopen_cfw_gx8002_crc32 = 0x102098a8;\n')
    linked = out/'header.elf'
    subprocess.run([pre+'ld', '-T', str(script), str(obj), '-o', str(linked)], check=True)
    target = Elf32(linked.read_bytes(), str(linked))
    for sec in target.sections:
        if target.relocations(sec['index']): raise ValueError('Probe unresolved relocations')
    counters = target.contents(next(sec for sec in target.sections if sec['name']=='.data'))
    if counters != bytes.fromhex('0400000004000000'): raise ValueError('Upstream header counters changed')
    (out/'header.linked.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(linked)],text=True))
    return {'sdk_commit': SDK_COMMIT, 'upstream_source_sha256': sha(data), 'probe_source_sha256':sha(c.read_bytes()),
            'compiled_bytes':len(elf.contents(section)), 'warning_policy':'Upstream signed/unsigned comparison remains a visible warning for this probe.', 'source_admitted':False, 'probe_address':0x10300000, 'counter_address':0x20026c74, 'crc_address':0x102098a8, 'linked_relocations':0,
            'limits':['Extracted upstream helper probe with external CRC binding, an isolated analysis address and fixed counter data. Stock helper is inlined; no standalone stock envelope or full behavioral equivalence claimed.']}

if __name__ == '__main__':
    report=build();(ROOT/'docs/research/gx8002-uart-header-upstream-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# SPDX-License-Identifier: MIT
"""Compose decoded BSS clear output with decoded public audio initialization.

This boundary check does not establish the actual reset-to-init call order.
"""
import json, subprocess
from compare_gx8002_system_initialize import verify as system_verify
from compare_gx8002_system_mpu import execute as system_execute
from compare_gx8002_clear_bss import verify as clear_verify, execute as clear_execute
from verify_gx8002_audio_output_public_init import verify as init_verify, execute as init_execute, ROOT, GLOBAL, DEFAULT, CALLBACK, sha
from verify_gx8002_memcpy_source import decode

def verify():
    clear = clear_verify()
    init = init_verify()
    system = system_verify()
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    clear_old = decode(subprocess.check_output([pre,'-D','--start-address=0x1553c','--stop-address=0x15560',str(ROOT/'build/gx8002-clear-bss/stock.elf')],text=True))
    clear_new = decode((ROOT/'build/gx8002-clear-bss/clear.disassembly.txt').read_text())
    init_old = decode(subprocess.check_output([pre,'-D','--start-address=0xeabc','--stop-address=0xeb00',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    init_new = decode((ROOT/'build/gx8002-audio-output-public-init/bits.disassembly.txt').read_text())
    cases = 0
    for clear_code, clear_entry, init_code, init_entry in ((clear_old,0x1553c,init_old,0xeabc),(clear_new,0x10023528,init_new,0x10205530)):
        for seed in (0,1,0xffffffff,0x55555555,0xaaaaaaaa,0x80000000):
            writes = clear_execute(clear_code,clear_entry,seed)
            global_writes = [value for address,value in writes if address == GLOBAL]
            if global_writes != [0]:
                raise ValueError('Dispatch slot not cleared exactly once')
            for mode in (0,1,2,3,0x80000000,0xffffffff):
                result, trace, pointer = init_execute(init_code,init_entry,mode,global_writes[0],None,CALLBACK,0)
                expected = [('read_global',0),('write_global',DEFAULT),('read_global',DEFAULT),('read_callback',DEFAULT+4,CALLBACK),('callback',CALLBACK,mode)]
                if (result,trace,pointer) != (0,expected,DEFAULT):
                    raise ValueError('Cleared dispatch initialization sequence')
                cases += 1
    system_old = decode(subprocess.check_output([pre,'-D','--start-address=0x15560','--stop-address=0x15604',str(ROOT/'build/gx8002-system/stock.elf')],text=True))
    system_new = decode((ROOT/'build/gx8002-system/system.disassembly.txt').read_text())
    mode_cases = 0
    for system_code, system_entry, delta, clear_code, clear_entry, init_code, init_entry in (
            (system_old,0x15560,0x1000dfec,clear_old,0x1553c,init_old,0xeabc),
            (system_new,0x1002354c,0,clear_new,0x10023528,init_new,0x10205530)):
        for start_mode in (0,1,2,0xffffffff):
            trace = system_execute(system_code,system_entry,{i:0 for i in (18,19,20,21)},True,start_mode,delta,0)
            clear_calls = trace.count(['call',0x10023528])
            if clear_calls != int(start_mode == 0):
                raise ValueError('Mode-dependent BSS clear')
            if clear_calls and trace.index(['call',0x10023528]) >= trace.index(['call',0x10025cbc]):
                raise ValueError('Clear must precede board initialization')
            for initial in (0,DEFAULT,0x20040000):
                state = initial
                if clear_calls:
                    state = dict(clear_execute(clear_code,clear_entry,0))[GLOBAL]
                expected_pointer = state or DEFAULT
                result, events, pointer = init_execute(init_code,init_entry,2,state,None,CALLBACK,0)
                expected_events = [('read_global',state)]
                if not state: expected_events.append(('write_global',DEFAULT))
                expected_events += [('read_global',expected_pointer),('read_callback',expected_pointer+4,CALLBACK),('callback',CALLBACK,2)]
                if (result,events,pointer) != (0,expected_events,expected_pointer):
                    raise ValueError('Mode-dependent dispatch preservation')
                mode_cases += 1
    return {'mode_compositions':mode_cases, 'system_evidence':system, 'decoded_compositions':cases, 'global_address':GLOBAL,
            'bss_clear_evidence':clear, 'public_init_evidence':init,
            'source_sha256':sha(__import__('pathlib').Path(__file__).read_bytes()),
            'hardware_qualified':False, 'source_only':False,
            'limits':['Mode compositions assume no dispatch writes in modeled board initialization or between system and audio init; these paths remain unqualified.',
                      'Does not establish reset reachability, physical RAM behavior or boot copy ordering.',
                      'Hardware initialization callback modeled; dispatch table separately source admitted.']}
if __name__ == '__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-audio-output-cleared-dispatch-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['decoded_compositions'],'clear compositions;',report['mode_compositions'],'mode compositions passed')

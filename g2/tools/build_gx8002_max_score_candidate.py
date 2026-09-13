#!/usr/bin/env python3
"""Build an authenticated upstream MAX scorer candidate; no source admission."""
import json
import re
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    out = ROOT / 'build/gx8002-max-score'
    out.mkdir(exist_ok=True)
    contents, dependencies = {}, []
    for rel in ('lvp/vui/kws/max_decoder.c', 'include/lvp_param.h',
                'include/lvp_context.h', 'lvp/vui/kws/kws_strategy.h', 'LICENSE'):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse',
                                       SDK_COMMIT + ':' + rel], text=True).strip()
        data = authenticated_blob(sdk / rel, blob)
        contents[rel] = data.decode()
        dependencies.append({'path': rel, 'blob': blob, 'sha256': sha(data)})
    text = contents['lvp/vui/kws/max_decoder.c']
    function = text[text.index('static int _LvpDoMaxScore('):text.index('\nint LvpDoMaxDecoder(')]
    function = function.replace('static int _LvpDoMaxScore', 'int open_cfw_gx8002_max_score', 1)
    first = function.index('        if ((threshold > 100)')
    last = function.index('        if ((score > threshold)', first)
    function = function[:first] + function[last:]
    diagnostic = '            printf (LOG_TAG"Greater than the score threshold! th:%d,S:%d,D:%d\\n", threshold, score, score - threshold);'
    if function.count(diagnostic) != 1:
        raise ValueError('upstream diagnostic changed')
    function = function.replace(diagnostic, '')
    types = []
    for name in ('LVP_KWS_PARAM', 'LVP_KWS_PARAM_LIST'):
        matches = re.findall(r'typedef struct \{[^}]*\} ' + name + ';', contents['include/lvp_param.h'])
        if len(matches) != 1:
            raise ValueError('parameter type changed')
        types.append(matches[0])
    prefix = '''/* Generated from authenticated NationalChip upstream; see candidate report. */
#include <stddef.h>
#include <stdint.h>
#define CONFIG_LVP_ENABLE_KEYWORD_RECOGNITION 1
#define CONFIG_LVP_ENABLE_BUNKWS_BIONIC 1
#define CONFIG_KWS_MAX_DECODER_WIN_LENGTH 10
#define CONFIG_MODEL_ACTIVATION_NUMBERS 1
#define MODEL_OUTPUT_LENGTH 2
#define LOG_TAG "[LVP_MAX_DECODE]"
/* Field projections of the recovered target ABI, not whole SDK objects. */
typedef struct { unsigned char reserved[68]; unsigned int snpu_buffer_size; } LVP_CONTEXT_HEADER;
typedef struct { LVP_CONTEXT_HEADER *ctx_header; unsigned int frame_index, ctx_index;
    unsigned char vad_flags, kws; unsigned short remaining_flags; void *snpu_buffer; } LVP_CONTEXT;
_Static_assert(offsetof(LVP_CONTEXT,kws)==13,"context kws");
_Static_assert(offsetof(LVP_CONTEXT,snpu_buffer)==16,"context buffer");
extern void *memset(void *, int, size_t);
extern int printf(const char *, ...);
extern void gx_dcache_invalid_range(unsigned int *, unsigned int);
extern void *LvpCTCModelGetSnpuOutBuffer(void *);
extern int s_max_decoder_window[10][2], s_max_score, s_max_index;
extern uint8_t activation_flag[2];
'''
    prototypes = '\n'.join(line for line in contents['lvp/vui/kws/kws_strategy.h'].splitlines()
                           if any(line.startswith(t) for t in (
                               'void KwsStragegyInsertKwsActivation(',
                               'float KwsStrategyGetBunkwsThresholdOffset(',
                               'void KwsStrategyClearBunkwsThresholdOffset(',
                               'int KwsStrategyRunBionic(')))
    source = out / 'candidate.c'
    source.write_text(prefix + '\n'.join(types) + '\n' + prototypes + '''
extern LVP_KWS_PARAM_LIST g_kws_list;
_Static_assert(sizeof(LVP_KWS_PARAM)==88,"keyword size");
_Static_assert(offsetof(LVP_KWS_PARAM,threshold)==76,"keyword threshold");
''' + function)
    bindings = {'activation_flag': 0x2002e744, 's_max_index': 0x2002e748,
                's_max_decoder_window': 0x2002e74c, 'g_kws_list': 0x2002e79c,
                's_max_score': 0x2002e7a4, 'memset': 0x102099cc,
                'gx_dcache_invalid_range': 0x10025608,
                'LvpCTCModelGetSnpuOutBuffer': 0x10208c60,
                'KwsStrategyRunBionic': 0x10208b78,
                'KwsStrategyGetBunkwsThresholdOffset': 0x10208b58,
                'KwsStragegyInsertKwsActivation': 0x10208980,
                'KwsStrategyClearBunkwsThresholdOffset': 0x10208b68,
                'printf': 0x10206c24}
    linker = out / 'candidate.ld'
    linker.write_text('SECTIONS { .text 0x102086dc : { *(.text.open_cfw_gx8002_max_score) }\n'
                      '.rodata 0x1020b276 : { *(.rodata*) } }\n' +
                      ''.join(f'{n} = {a:#x};\n' for n, a in bindings.items()))
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    flags = ['-Os', *FLAGS[1:], '-Wno-error=sign-compare']
    obj, elf = out / 'candidate.o', out / 'candidate.elf'
    subprocess.run([pre+'gcc', *flags, '-c', str(source), '-o', str(obj)], check=True)
    subprocess.run([pre+'ld', '-T', str(linker), str(obj), '-o', str(elf)], check=True)
    parsed = Elf32(elf.read_bytes(), str(elf))
    section = next(s for s in parsed.sections if s['name'] == '.text')
    if any(s['name'] and s['section'] == 0 for s in parsed.symbols()):
        raise ValueError('unresolved scorer symbols')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elf)],text=True))
    report = {'sdk_commit': SDK_COMMIT, 'dependencies': dependencies, 'flags': flags,
              'source_sha256': sha(source.read_bytes()), 'compiled_bytes': section['size'],
              'stock_envelope_bytes': 420, 'fits': section['size'] <= 420,
              'source_admitted': False,
              'changes_from_upstream': ['Remove Similar and Greater diagnostic branches absent from stock.'],
              'limits': ['Candidate only: floating-point behavior, helper mutations, ABI and string ownership require qualification.']}
    (ROOT/'docs/research/gx8002-max-score-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

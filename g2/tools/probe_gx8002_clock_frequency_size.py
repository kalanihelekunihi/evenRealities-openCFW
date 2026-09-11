# SPDX-License-Identifier: MIT
"""Isolated source-level size probe; never emits a firmware provider."""
import json
import subprocess
from pathlib import Path
from build_gx8002_clock_frequency_candidate import build, ROOT, Elf32, sha


def probe():
    baseline=build()
    out=ROOT/'build/gx8002-clock-frequency-size-probe'
    out.mkdir(exist_ok=True)
    header=(ROOT/'build/gx8002-clock-frequency/clk_priv_frequency.h').read_text()
    start=header.index('\t\t\tswitch (vco_subband) {',header.index('static inline unsigned int _clk_get_module_frequence'))
    end=header.index('\n\n\t\t\tfin =',start)
    old=header[start:end]
    assert all(str(v) in old for v in (61440000,73728000,86016000,98304000))
    header=header[:start]+'\t\t\tfvco = 61440000u + vco_subband * 12288000u;'+header[end:]
    early = """module >= CLOCK_MODULE_SCPU ||
				module == CLOCK_MODULE_SRAM ||
				module == CLOCK_MODULE_OSC_REF ||
				module == CLOCK_MODULE_AUDIO_IN_SYS"""
    if header.count(early) != 1:
        raise ValueError('Early-return adaptation anchor')
    header = header.replace(early, '(unsigned int)module >= 9u || (((unsigned int)module & ~4u) == 2u)')
    (out/'clk_priv_frequency.h').write_text(header)
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    obj=out/'frequency.o'
    subprocess.run([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-gcc'),*baseline['flags'],
        '-isystem',str(out),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),
        '-c',str(ROOT/'components/shared/gx8002/runtime_gx8002_clock_frequency.c'),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj))
    section=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_clock_frequency')
    report={'baseline_bytes':480,'probe_bytes':section['size'],'envelope_bytes':444,
        'adaptation':'Replace four masked PLL subband cases with exact base-plus-step arithmetic; express equivalent low-frequency module predicate as stock comparison and bit clear.',
        'adapted_header_sha256':sha(header.encode()),'source_admitted':False,
        'limits':['Unlinked size probe only; no decoded or ABI qualification.']}
    (ROOT/'docs/research/gx8002-clock-frequency-size-probe.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(probe(),indent=2))

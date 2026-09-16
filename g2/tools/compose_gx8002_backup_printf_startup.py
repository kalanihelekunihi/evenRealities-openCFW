# SPDX-License-Identifier: MIT
"""Prepare formatter dependency sections for the startup source link."""
import re,subprocess
from build_gx8002_backup_printf_source_cluster import build,ROOT,Elf32


def prepare(out,pre):
    evidence=build()
    base=ROOT/'build/gx8002-backup-printf-source-cluster'
    script=(base/'cluster.ld').read_text()
    script=script.replace((ROOT/'build/gx8002-backup-unsigned-division/division.ld').read_text(),'')
    # Startup already owns these verified integer/reverse/division components.
    for name in ('integer_format','long','wide','reverse'):
        script=re.sub(r'SECTIONS \{ \.printf_'+name+r' .*?\nASSERT\([^\n]+\n','',script)
    for name in ('integer','reverse'):
        script=script.replace(str(base/(name+'.o'))+'(.text* .rodata*)','')
    inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    copied=[]
    for i,path in enumerate(inputs):
        dest=out/f'formatter-dependency-{i}.o'
        # Arithmetic uses its compact source copy at its own qualified address;
        # keep that separate from startup's general-purpose memcpy alias.
        subprocess.run([pre+'objcopy','--redefine-sym','memcpy=formatter_arithmetic_memcpy',path,str(dest)],check=True)
        script=script.replace(path,str(dest));copied.append(str(dest))
    return evidence,script,copied


def verify(elf,evidence):
    base=ROOT/'build/gx8002-backup-printf-source-cluster'
    original=Elf32((base/'cluster.elf').read_bytes(),'formatter')
    aliases={'.printf_integer_format':'.printf_format','.printf_wide':'.printf_long_long'}
    for section in original.sections:
        if section['flags']&2 and section['size']:
            target=aliases.get(section['name'],section['name'])
            linked=next(s for s in elf.sections if s['name']==target)
            assert linked['address']==section['address'] and elf.contents(linked)==original.contents(section),target
    symbols={s['name']:s for s in elf.symbols() if s['name']}
    for name in evidence['required_source_symbols']:
        assert symbols[name]['section'] not in (0,0xfff1),name
    assert symbols['_vsnprintf']['value']==0x10008e20

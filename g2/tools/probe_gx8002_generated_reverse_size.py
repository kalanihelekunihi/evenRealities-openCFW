# SPDX-License-Identifier: MIT
"""Measure scalar permutation variants without changing the FFT candidate."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,FLAGS,Elf32,sha

def probe():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_bit_reverse_256.c';base=source.read_text()
    old='''    for (unsigned i = 0; i < 256; ++i) {
        unsigned reversed = 0, value = i;
        for (unsigned bit = 0; bit < 8; ++bit) {
            reversed = (reversed << 1) | (value & 1);
            value >>= 1;
        }'''
    new='''    unsigned reversed = 0;
    for (unsigned i = 1; i < 256; ++i) {
        unsigned bit = 128;
        while (reversed & bit) { reversed ^= bit; bit >>= 1; }
        reversed ^= bit;'''
    old_swap='''            int16_t real = samples[2 * i], imag = samples[2 * i + 1];
            samples[2 * i] = samples[2 * reversed];
            samples[2 * i + 1] = samples[2 * reversed + 1];
            samples[2 * reversed] = real;
            samples[2 * reversed + 1] = imag;'''
    new_swap='''            typedef uint32_t alias_word __attribute__((may_alias));
            alias_word *words = (alias_word *)samples;
            uint32_t value = words[i];
            words[i] = words[reversed];
            words[reversed] = value;'''
    assert old in base and old_swap in base
    variants={'baseline':base,'incremental':base.replace(old,new),'word_swap':base.replace(old_swap,new_swap),'incremental_word':base.replace(old,new).replace(old_swap,new_swap)}
    out=ROOT/'build/gx8002-generated-reverse-size-probe';out.mkdir(exist_ok=True);rows=[]
    for name,text in variants.items():
        path=out/(name+'.c');path.write_text(text);obj=out/(name+'.o')
        subprocess.run([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-gcc'),'-Os',*FLAGS[1:],'-c',str(path),'-o',str(obj)],check=True)
        elf=Elf32(obj.read_bytes(),name)
        rows.append({'variant':name,'source_sha256':sha(path.read_bytes()),'object_sha256':sha(obj.read_bytes()),'code_bytes':sum(s['size'] for s in elf.sections if s['flags']&4)})
    result={'baseline_source_sha256':sha(source.read_bytes()),'variants':rows,'source_admitted':False,'limits':['Size-only variants; word accesses require original word alignment. Behavior and linked layout not qualified by this probe.']}
    (ROOT/'docs/research/gx8002-generated-reverse-size-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print([(r['variant'],r['code_bytes']) for r in probe()['variants']])

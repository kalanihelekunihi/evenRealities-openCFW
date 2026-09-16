# SPDX-License-Identifier: MIT
"""Execute source remainder and reconstructed arithmetic on exceptional inputs."""
import json, random, subprocess
from build_gx8002_backup_cfft import ROOT, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_muldiv_nonfinite import oracle, INF, MASK
from analyze_gx8002_double_wrapper_references import analyze


def verify():
    code, readonly, hashes = {}, {}, {}
    for stem, filename in [('gx8002-fmod-placed','fmod.elf'), ('gx8002-double-muldiv-corrected','muldiv.elf')]:
        path = ROOT/'build'/stem/filename
        report = json.loads((ROOT/'docs/research'/(stem+'.json')).read_text())
        assert sha(path.read_bytes()) == report['elf_sha256']
        hashes[stem] = report['elf_sha256']
        elf = Elf32(path.read_bytes(), stem)
        decoded = decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'), '-d', str(path)], text=True))
        assert not set(code).intersection(decoded)
        code.update(decoded)
        for section in elf.sections:
            if section['flags'] & 2 and section['size'] and section['type'] != 8:
                readonly.update({section['address']+i:b for i,b in enumerate(elf.contents(section))})
    rng = random.Random(804576)
    payloads = [0,1,(1<<52)-1]+[1<<i for i in range(52)]+[rng.getrandbits(52) for _ in range(32)]
    special = [(s<<63)|INF|p for s in (0,1) for p in payloads]+[0,1<<63]
    other = [0,1,1<<63,0x3ff0000000000000,0xbff0000000000000,0x7fefffffffffffff,INF,INF|(1<<63),INF|123,0xfff8000000000123]
    pairs = [(a,b) for a in special for b in other]+[(b,a) for a in special for b in other]
    count = 0
    for a,b in pairs:
        x,y = a&MASK,b&MASK
        invalid = y == 0 or x >= INF or y > INF
        if invalid:
            product = oracle('mul',a,b)
            expected = oracle('div',product,product)
        else:
            assert x == 0 or y == INF
            expected = a
        actual = execute(code,0x495e4+0x10003000-0x3b940,bytes(20),arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32],return_pair=True,readonly=readonly,max_steps=10000)
        assert actual == expected,(hex(a),hex(b),hex(actual),hex(expected))
        count += 1
    references = analyze(0x495e4,0x49828)
    assert not references['external_literal_pools'] and not references['stored_address_words']
    result = {'source_elf_hashes':hashes,'cases':count,'references':references,'source_admitted':False,'limits':['Executes complete source remainder and corrected source multiply/divide/pack/unpack. Oracle preserves those upstream NaN payload/sign conventions. Stock exceptional behavior, floating-point flags, computed references and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-fmod-special.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__ == '__main__':
    print(verify())

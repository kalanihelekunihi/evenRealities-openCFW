# SPDX-License-Identifier: MIT
"""Execute placed fmod against exact integer significand remainder."""
import json, random, subprocess
from build_gx8002_backup_cfft import ROOT, sha, IMAGE, IMAGE_SHA, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute


def dyadic(bits):
    exponent = (bits >> 52) & 2047
    return ((bits & ((1 << 52)-1)) | ((1 << 52) if exponent else 0),
            exponent - 1075 if exponent else -1074)


def reference(a, b):
    x, xp = dyadic(a)
    y, yp = dyadic(b)
    common = min(xp, yp)
    remainder = (x << (xp-common)) % (y << (yp-common))
    sign = a & (1 << 63)
    if not remainder:
        return sign
    top = remainder.bit_length()-1 + common
    if top < -1022:
        return sign | (remainder << (common+1074))
    shift = remainder.bit_length()-53
    if shift > 0:
        assert remainder & ((1 << shift)-1) == 0
        significand = remainder >> shift
    else:
        significand = remainder << -shift
    return sign | ((top+1023) << 52) | (significand & ((1 << 52)-1))


def verify():
    path = ROOT/'build/gx8002-fmod-placed/fmod.elf'
    report = json.loads((ROOT/'docs/research/gx8002-fmod-placed.json').read_text())
    assert sha(path.read_bytes()) == report['elf_sha256']
    code = decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'), '-d', str(path)], text=True))
    stock = IMAGE.read_bytes(); assert sha(stock) == IMAGE_SHA
    wrapper = ROOT/'build/gx8002-board/padmux-get-stock.elf'
    stock_elf = Elf32(wrapper.read_bytes(), 'stock')
    assert stock_elf.contents(next(s for s in stock_elf.sections if s['name']=='.data')) == stock
    old = decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'), '-D', '--start-address=0x495e4', '--stop-address=0x49828', str(wrapper)], text=True))
    readonly = {0x10003000+i:b for i,b in enumerate(stock[0x3b940:0x4f9cc])}
    edge = [(s << 63) | (e << 52) | f for s in (0,1) for e in (0,1,2,1022,1023,1024,2045,2046) for f in (0,1,1 << 51,(1 << 52)-1)]
    pairs = [(a,b) for a in edge for b in edge if b & ((1 << 63)-1)]
    rng = random.Random(804576)
    pairs += [(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(1000)]
    count = 0
    for a,b in pairs:
        if ((a >> 52)&2047)==2047 or ((b >> 52)&2047)==2047 or not b & ((1 << 63)-1):
            continue
        actual = execute(code, 0x495e4+0x10003000-0x3b940, bytes(20), arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32], return_pair=True, max_steps=100000)
        original = execute(old, 0x495e4, bytes(20), arguments=[a&0xffffffff,a>>32,b&0xffffffff,b>>32], return_pair=True, readonly=readonly, max_steps=100000)
        expected = reference(a,b)
        assert actual == original == expected, (hex(a),hex(b),hex(actual),hex(expected))
        count += 1
    result = {'source_elf_sha256': report['elf_sha256'], 'finite_cases': count, 'stock_sha256': IMAGE_SHA, 'stock_comparison_cases': count, 'oracle': 'Exact integer dyadic remainder with dividend sign, including signed zero; no floating-point host arithmetic.', 'source_admitted': False, 'limits': ['Decoded placed source and stock both match exact finite remainder, with ABI checks. Nonfinite inputs, zero divisors, reference census and hardware remain separate.']}
    (ROOT/'docs/research/gx8002-fmod-finite.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__ == '__main__':
    print(verify())

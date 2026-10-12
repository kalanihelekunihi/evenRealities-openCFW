#!/usr/bin/env python3
"""Check the pinned generic FLS branch against the selected builtin formula."""
import json
import random


def generic(word):
    bit = 32
    if word == 0:
        bit -= 1
    for mask, shift in ((0xffff0000, 16), (0xff000000, 8),
                        (0xf0000000, 4), (0xc0000000, 2),
                        (0x80000000, 1)):
        if not word & mask:
            word = (word << shift) & 0xffffffff
            bit -= shift
    return bit - 1


rng = random.Random(0x4169a4)
values = [0, 1, 2, 3, 0x80000000, 0xffffffff]
values.extend(rng.getrandbits(32) for _ in range(100000))
for word in values:
    assert generic(word) == word.bit_length() - 1
print(json.dumps({"status": "PASS_BOUNDED_TLSF_FLS_BRANCH",
                  "cases": len(values),
                  "limits": "Pure value equality; target retained CLZ and zero guard require separate source map evidence."}))

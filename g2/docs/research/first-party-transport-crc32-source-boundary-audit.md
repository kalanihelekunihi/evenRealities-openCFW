# First-party transport CRC-32 source boundary audit

Status: production. The Even Realities G2 `2.2.6.10` first-party transport
CRC-32 update is source-owned in the `linux-clang` core overlay and redirected
live; the canonical `apple-clang` reference is unchanged. Run addresses use
`run = file_offset + 0x00437FE0`.

## Function

The standard reflected CRC-32 (polynomial `0xEDB88320`, seed and final XOR
`0xFFFFFFFF`) backs first-party transport-protocol packet framing, OTA
external-flash verification, and the box-UART manager. It is distinct from the
already-replaced non-reflected CRC-32C (`efs_crc32c`, polynomial `0x1EDC6F41`).

The 256-entry reflected table is stored as constant data at run `0x006987A8`
(file `0x2607C8`, 1024 bytes, SHA-256
`12f3e0576d447eb37b36d82ba0c1c5481b8f0d12fdc70347ce4a076b229d4c86`). It is the
canonical CRC-32 table: `research/candidates/first_party_crc32.c` regenerates it
byte-for-byte from the polynomial (see
[`first-party-frontier-ranking.md`](first-party-frontier-ranking.md)), so it is
known constant data rather than an opaque blob.

## Recovered stock body and ABI

The update function is a single standalone body at `[0x0058FCF0,0x0058FD18)`,
40 bytes, SHA-256
`232e226bd1ece2ee0d8a14abc3461651743ef4c987b46406fc2995154ed59a29`, followed by
its 4-byte table-base literal at `0x0058FD18`. Focused disassembly:

```text
0x0058FCF0  push {r4, r5}
0x0058FCF2  b    0x0058FD0A            ; enter loop condition (handles len == 0)
0x0058FCF4  ldr  r4, [0x0058FD18]      ; table base 0x006987A8
0x0058FCF6  ldrb r5, [r2]              ; r5 = *data
0x0058FCF8  movs r3, r0                ; r3 = crc
0x0058FCFA  uxtb r3, r3                ; r3 = crc & 0xFF
0x0058FCFC  eors r5, r3                ; r5 = (*data ^ (crc & 0xFF)) & 0xFF
0x0058FCFE  ldr.w r3, [r4, r5, lsl 2]  ; r3 = table[index]
0x0058FD02  eors.w r0, r3, r0, lsr 8   ; crc = table[index] ^ (crc >> 8)
0x0058FD06  adds r2, r2, 1             ; ++data
0x0058FD08  subs r1, r1, 1             ; --len
0x0058FD0A  cmp  r1, 0
0x0058FD0C  bne  0x0058FCF4
0x0058FD0E  movs.w r1, -1
0x0058FD12  eors r0, r1                ; crc ^= 0xFFFFFFFF
0x0058FD14  pop  {r4, r5}
0x0058FD16  bx   lr
```

Recovered ABI: `r0` = seed CRC, `r1` = length, `r2` = data pointer; returns
`(table-updated CRC) ^ 0xFFFFFFFF`. The seed of `0xFFFFFFFF` is supplied by the
caller, and the final XOR is applied inside the body.

## Caller topology

Exactly one direct `BL` caller, at run `0x00579856`:

```text
0x00579852  ldr  r2, [r6]             ; r2 = data pointer
0x00579854  ldr  r1, [r7]             ; r1 = length
0x00579856  movs.w r0, -1             ; r0 = 0xFFFFFFFF seed
0x00579856  bl   0x0058FCF0
0x0057985A  str  r0, [sp, 0x14]       ; store finalised CRC
```

So `f(0xFFFFFFFF, len, data)` is the canonical CRC-32, with check value
`0xCBF43926` over `"123456789"`. No other direct, interior, or stored entry
reaches the body.

## Source replacement

`components/apollo_main/core_overlay/runtime_transport_crc32.c`
(`open_cfw_transport_crc32_update`) re-expresses the recovered algorithm in
clean-room C. Under the reviewed `linux-clang` flags it compiles to a 38-byte,
relocation-free Thumb leaf (only a discarded `.ARM.exidx` entry), loading the
table base `0x006987A8` via `movw`/`movt` exactly as the stock body loads it
from its literal pool. The table remains pinned official compatibility data.

The leaf is gated to the `linux-clang` profile. The patch site
`replace_transport_crc32_update` validates the 40-byte stock body against its
SHA-256 and installs a `B.W` tail-branch at `0x0058FCF0` to the leaf; the leaf
returns through the preserved `LR` to the sole caller. Under `apple-clang` the
leaf, patch site, and function are filtered out, leaving the canonical
overlay/component/package pins byte-identical.

## Verification

- `make source verify` reproduces the `linux-clang` core-source package
  fail-closed with the live redirect.
- The rebuilt component contains the `B.W` at `0x0058FCF0` targeting the leaf,
  whose body hashes to the recorded pin.
- `tests/test_first_party_transport_crc32_leaf.py` pins the stock body and
  table, checks the profile gating both ways, and compiles the exact leaf
  source against the firmware's own table to prove it computes the canonical
  CRC-32 (check value `0xCBF43926`).

No hardware, serial port, debugger, or flasher is touched.

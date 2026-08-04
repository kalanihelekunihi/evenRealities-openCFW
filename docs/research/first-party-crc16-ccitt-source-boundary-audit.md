# First-party CRC-16/CCITT source boundary audit

Status: production. The Even Realities G2 `2.2.6.10` first-party CRC-16/CCITT
computation (both stock variants) is source-owned in the `linux-clang` core
overlay and redirected live; the canonical `apple-clang` reference is unchanged.
Run addresses use `run = file_offset + 0x00437FE0`.

## Function family

CRC-16/CCITT (polynomial `0x1021`, MSB-first, non-reflected, no final XOR). The
firmware ships two byte-identical copies of the 256-entry `0x1021` forward table
at run `0x006C0350` and `0x006C0B50` (512 bytes each, SHA-256
`ea5f177f22d32b7e80c132b498ee4b92882484f891f43f1897075f28bb3da4d9`), each used
by one table-driven update function. The table equals a from-polynomial
regeneration (`t[1]=0x1021`, `t[2]=0x2042`, …), so it is known constant data
rather than an opaque blob.

This is distinct from the already-source-owned TinyFrame CRC-16/ARC
(`0xA001`, reflected) and the CRC-32/CRC-32C boundaries.

## Recovered stock bodies and ABIs

### Variant A — XMODEM (seed `0x0000`)

`[0x0059D350,0x0059D37C)`, 44 bytes, SHA-256
`e6140b25efec9859630cd8a79079243322694e7d7a632ad9e6a4a82457cee999`, table
`0x006C0350`, two direct callers (`0x00595A6A`, `0x00595DD8`).

```text
push {r4,r5,r6}
r2 = data (arg0); crc(r0) = 0; i(r4) = 0
loop:  r5 = crc & 0xFFFF
       r6 = *data ^ (crc >> 8)
       crc = table[r6] ^ (crc << 8);  ++data; ++i
       while (i < len)               ; signed compare
crc &= 0xFFFF; return crc
```

ABI: `uint16_t f(const uint8_t *data, int len)`, seed `0x0000`, no final XOR.
Check value `0x31C3` over `"123456789"`.

### Variant B — CCITT-FALSE / resumable (seed `*ptr` or `0xFFFF`)

`[0x0049ACD4,0x0049AD08)`, 52 bytes, SHA-256
`52c3def4c908a312e9ea66015188a2cc93d3dc23254a8fa8836d3e1bf0caaee1`, table
`0x006C0B50`, 48 direct callers.

```text
push {r4,r5,r6}
r3 = data (arg0)
crc(r0) = (seed(r2) == 0) ? 0xFFFF : *(uint16*)seed
i(r4) = 0
loop:  crc = table[(*(data+i)) ^ (crc >> 8)] ^ (crc << 8);  ++i
       while (i < len)               ; unsigned compare
crc &= 0xFFFF; return crc
```

ABI: `uint16_t f(const uint8_t *data, uint32_t len, const uint16_t *seed)`. A
null `seed` seeds `0xFFFF` (CRC-16/CCITT-FALSE, check value `0x29B1` over
`"123456789"`); a non-null `seed` resumes from `*seed`, so callers can CRC a
buffer in successive chunks.

## Source replacement

`components/apollo_main/core_overlay/runtime_crc16_ccitt.c`
(`open_cfw_crc16_ccitt_xmodem`, `open_cfw_crc16_ccitt`) re-expresses both
recovered algorithms in clean-room C. Under the reviewed `linux-clang` flags
each compiles to a relocation-free Thumb leaf (56 and 54 bytes; only discarded
`.ARM.exidx` entries), loading its table base via `movw`/`movt` exactly as the
stock bodies do. The tables remain pinned official compatibility data.

Both leaves are gated to the `linux-clang` profile. The patch sites
`replace_crc16_ccitt_xmodem` and `replace_crc16_ccitt` validate the stock
bodies against their SHA-256 and install `B.W` tail-branches at `0x0059D350`
and `0x0049ACD4`; the leaves return through the preserved `LR` to all callers.
Under `apple-clang` the leaves, patch sites, and functions are filtered out,
leaving the canonical overlay/component/package pins byte-identical.

## Verification

- `make source verify` reproduces the `linux-clang` core-source package
  fail-closed with both live redirects.
- The rebuilt component contains `B.W` at `0x0059D350` and `0x0049ACD4`
  targeting the two leaves, whose bodies hash to the recorded pins.
- `tests/test_first_party_crc16_ccitt_leaf.py` pins the stock bodies and
  tables, checks the profile gating both ways, and compiles the exact leaf
  source against the firmware's own table to prove the XMODEM (`0x31C3`) and
  CCITT-FALSE (`0x29B1`) check values plus the resumable-seed contract.

No hardware, serial port, debugger, or flasher is touched.

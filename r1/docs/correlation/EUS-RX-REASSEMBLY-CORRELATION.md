# EUS receive reassembly correlation

## Decision

The 424-byte body at `0x00032198..<0x00032340` is R1 product-specific EUS receive
reassembly and outer-checksum policy. It has one direct caller, the custom-service event callback
at callsite `0x0005D69C`, where service event `3` routes channel-2 data into this function.
No third-party implementation is identified.

The function is classified `r1_product_specific` with disposition
`clean_room_behavior_only_security_preserving`. The clean implementation is
`r1/src/r1_protocol.c::r1_reassembler_feed`; toolchain memory movement, FreeRTOS allocation,
and Nordic logging remain separately owned provider dependencies.

## Exact recovered body

| Entry | Bytes | SHA-256 | Direct callers |
| --- | ---: | --- | --- |
| `0x00032198` | 424 | `a91ae73ec32df232276ab2e01dcd4c4e29f864de03b66f5addcea96350688df5` | `0x0005D69C` |

The recovered wire contract is a five-byte fragment header: descending one-byte sequence, a
little-endian four-byte CRC-32/Castagnoli value, then at most 239 payload bytes. Sequence zero
terminates a train. The accepted first sequence is `0...16`, yielding at most 17 fragments and
4,063 inbound logical bytes. The checksum primitive is the separately admitted R1 body at
`0x0005D8A4`: MSB-first polynomial `0x1EDC6F41`, zero seed, and no final XOR.

## Recovered behavior and deliberate hardening

Stock allocates `(first_sequence + 1) * 239` bytes for first sequences `2...16`, uses a static
buffer for sequence `1`, and checks a sequence-zero single fragment directly. A repeated fragment
with the same sequence rewinds the previous contribution and replaces it. The stock body does not
enforce strict descending continuity or repeated-checksum consistency before the terminal CRC
test. It releases a dynamically allocated buffer after the terminal fragment and sends a six-byte
transport error through its injected callback if the outer checksum fails.

openR1 preserves the valid wire behavior while making state per-link and allocation-free. It
rejects duplicate or discontinuous sequences, inconsistent repeated checksums, oversized trains,
and checksum failures before inner-model dispatch. This is an intentional security-audit
hardening; permissive malformed-train behavior is not compatibility functionality.

## Verification

```sh
python3 tools/evidence/summarize_r1_eus_rx_reassembly.py
```

The read-only summarizer pins the application image, exact body, sole caller, bounds, checksum
contract, provider split, and hardening decision. Host and sanitizer tests cover valid single- and
multi-fragment trains, the exact-multiple empty terminal fragment, all boundary lengths, duplicate
rejection, and cross-fragment checksum inconsistency rejection.

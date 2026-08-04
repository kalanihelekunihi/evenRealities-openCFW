# Nanopb `pb_decode_varint32()` source-candidate audit

Status: qualified as a production-excluded candidate. This work makes no
overlay, manifest, build, provenance, or snapshot-verifier registration.

## Result

The stock wrapper at `[0x0048F5AE, 0x0048F5B8)` is compatible with nanopb
0.4.7 through 0.4.9 `pb_decode_varint32()`. It forwards the stream and
destination to private `pb_decode_varint32_eof()` while passing a null EOF
pointer, then returns that seam's Boolean result unchanged.

The candidate is uniquely named
`open_cfw_nanopb_decode_varint32_source_candidate()` and remains excluded from
production. Its only undefined dependency is
`open_cfw_nanopb_decode_varint32_eof_stock_candidate()`, the future binding for
stable stock entry `0x0048F4B8`. This is distinct from the public 64-bit
`pb_decode_varint()` body beginning at `0x0048F5B8`.

## Authenticated upstream identity

The exact 132-byte pristine definition has SHA-256
`ef3f2bd19c12b07ca055ab63f8e82ea6f4b34e67aefb277435092e7485834f0f`
in every checked release:

| Release | Commit | `pb_decode.c` byte span |
|---|---|---:|
| nanopb-0.4.7 | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `[7399, 7531)` |
| nanopb-0.4.8 | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `[7399, 7531)` |
| nanopb-0.4.9 | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `[7485, 7617)` |

The vendored authenticated snapshot selects nanopb-0.4.9. The shared release
definition is compatibility evidence, not proof of the vendor's historical
checkout.

## Stock boundary, ingress, and outgoing closure

The official application body is 10 bytes with SHA-256
`48218a658cffd7aeddfb623c9d0e7bd038ceb2a6898e9f8d08b10d5779f4f79b`.
It has exactly six direct `BL` callers:

- `0x0048F654`
- `0x0048F788`
- `0x00490132`
- `0x00490362`
- `0x004903F6`
- `0x00490546`

Its complete outgoing closure is the single
`BL 0x0048F5B2 → 0x0048F4B8`. A halfword-aligned scan found no external
`B.W`, conditional-wide, narrow-branch, stored-function-pointer, or interior
entry into the wrapper span. A future promotion can therefore replace the
complete 10-byte stock span with a `B.W` trampoline and NOP fill; this
candidate installs no trampoline.

## ABI and host behavior

The recovered target contract uses the standard Thumb C first-three-argument
registers: stream in `r0`, `uint32_t *` destination in `r1`, and null
`bool *eof` in `r2`; Boolean results return through `r0`. Target-only static
assertions retain the recovered one-byte `bool` and four-byte `uint32_t`
widths, while the imported stream header retains the reviewed four-word
callback-stream layout.

The host differential fixture exercises the real authenticated upstream
public wrapper for zero, 127, 128, `UINT32_MAX`, empty input, truncated input,
and overflow. It then verifies that the candidate forwards exactly the
upstream result and destination behavior through one seam call with a null EOF
pointer.

With the pinned Apple clang 21 target profile, two independent builds produce
the same 988-byte ELF object with SHA-256
`d67a6c3eb4467dc5d5d52dd7334bfc689b7770365effc18eeab860e883ed0ea1`.
Its sole executable section is a six-byte tail-call wrapper with SHA-256
`e1306533deb7c78f8b3431ad297def9b17e14d91a575d167181bd7e0c1a1c546`.
The section has one `R_ARM_THM_JUMP24` relocation at offset 2 to the private
EOF seam, plus the expected unwind-index `R_ARM_PREL31` relocation and no
writable data.

## Bootloader exclusion and promotion gate

The authenticated bootloader contains neither the exact stock body nor its
seven-byte prefix and suffix probes. No bootloader homolog is claimed.

Production promotion remains gated on qualification or explicit stock binding
of private `pb_decode_varint32_eof()` at `0x0048F4B8`, followed by placed-object
relocation and aggregate overlay tests. The candidate alone cannot change a
flashable artifact.

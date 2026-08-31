# G2 touch shipped-prefix software-readiness ledger

This is a device-free, deterministic composition of the authenticated G2 touch
prefix evidence. It answers a narrower question than production readiness:
which shipped bytes and reachable functions presently have project source,
typed upstream/provider boundaries, intentional unsupported treatment, or no
sufficient classification?

> **Current Wave-0.5 correction.** This document begins with the historical
> first-pass ledger below. The current exhaustive classifier retains one
> 14,510-byte semantic stock-address candidate union, with pinned address and
> content digests, but no longer labels that union blanket OpenCFW/MIT. The
> machine-readable
> `tools/manifests/g2-touch-final-source-candidate-provenance.tsv` partitions it
> into non-overlapping source-route/license subrows. A translation unit's
> presence in the nonproduction source image is recorded separately from body
> or output identity; every subrow denies stock-address-to-linked-body proof,
> production-ELF ownership, and stock-byte license authority. Apache CAT2
> bodies that are merely identified upstream remain not linked as those
> bodies, and Infineon EULA comparison source remains excluded. The current
> physical bucket is still 14,510 bytes and completion still reports
> `candidate_source_not_routed=14,510`; this is an accounting correction, not a
> byte promotion or production-routing event.

The result is **not software-complete**. It performs no MMIO, reset, DFU,
signing, flash, or hardware operation and makes no hardware-validation claim.

## Authenticated scope

- FWPK SHA-256:
  `0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`
- Whole FWPK: 34,464 bytes
- Shipped type-3 payload: 34,432 bytes, offsets `0x0000..0x867f`
- Mixed code/pool span: 30,364 bytes, offsets `0x00c0..0x775b`
- Resident addresses at or above `0x8680` are outside the shipped payload and
  remain an unavailable external ABI. They contribute zero shipped bytes.

## Whole-blob physical-byte accounting

Every FWPK byte belongs to exactly one row in the byte manifest. Reachable
instruction address sets are deduplicated, so shared function tails are not
counted multiple times.

| Bucket | Physical bytes | Meaning |
|---|---:|---|
| Project source candidate | 816 | Reachable instructions with existing project-authored candidates |
| Typed external or unsupported | 8,946 | Provider/runtime code, fail-closed contracts, no-op logger, vectors, strings, and external configuration |
| Still unclassified | 24,190 | 24,048-byte mixed code/pool remainder plus 142 reachable vector-target bytes |
| Generated transport/fill | 512 | FWPK wrapper, zero/FF fill, and trailing checksum |
| **Total** | **34,464** | Exhaustive whole-FWPK accounting |

The 24,048-byte remainder must not be read as 24,048 bytes of undiscovered
functions. The authenticated region combines literal pools, read-only data,
unreachable code, and as-yet-undiscovered entry bodies. Separating those kinds
is required before a stronger source-closure claim is possible.

## Reachable mapped code

The conservative vector/evidence/direct-`BL` closure maps 6,316 unique physical
instruction bytes across 63 entries.

| Disposition | Functions | Physical instruction bytes |
|---|---:|---:|
| Existing project source candidate | 10 | 816 |
| Project fail-closed contract | 8 | 1,560 |
| Apache-2.0 upstream provider | 14 | 1,068 |
| ARM EABI/C runtime provider | 7 | 774 |
| Infineon-EULA provider; clean-room replacement required for MIT distribution | 20 | 1,948 |
| Intentional unsupported no-op logger | 1 | 8 |
| Still unclassified vector targets | 3 | 142 |
| **Mapped total** | **63** | **6,316** |

Function instruction sizes cannot be summed for physical coverage because
three vector targets share a suffix and other helper tails overlap. The byte
ledger uses address sets to count each shipped byte once.

## Source and provider disposition

The four implemented MIT policy helpers and four typed fail-closed policy
contracts are isolated in
`components/shared/touch/runtime_touch_policy_helpers.c`. Missing callbacks
return unavailable without fabricating application semantics.

Existing I2C protocol and sensing candidates are source-audited, and hardware
validation remains blocked by unavailable physical evidence. They are original openCFW
clean-room work containing no copied GPL or vendor source. The repository's
additional grant therefore supports `MIT OR GPL-3.0-only`, preserving the
existing GPL option while making the MIT option explicit. Provider and
authenticated firmware evidence licenses are unchanged.

Provider attribution is also license-specific:

- Infineon CAT2 PDL candidates are from the Apache-2.0 upstream provider and
  require its notices.
- CAPSENSE and Em_EEPROM comparison sources carry Infineon EULA terms. They are
  interface/identity evidence only unless those terms are accepted; an MIT
  public result needs independent clean-room implementations.
- ARM EABI/C helpers need a selected compiler/runtime implementation under its
  own upstream license. Stock bytes are not a distributable substitute.

Public symbol matches identify plausible provider boundaries, not a claim that
the pinned public commits are the exact historical stock source versions.

## Resident ABI and release gate

Six observed resident addresses (`0xaa5c`, `0xb0c4`, `0xb0e8`, `0xb374`,
`0xb4fc`, and `0xb51c`) and the unresolved resident DFU entry are not present in
the shipped type-3 payload. The readiness manifest therefore models them as typed,
zero-byte, external-unavailable ABI—not as recovered functions.

The software-complete gate stays closed until at least:

1. the 24,048-byte mixed remainder is separated into code, pools, and data and
   remaining function entries are discovered;
2. the roles of the three shared-suffix vector targets are resolved;
3. CAPSENSE and Em_EEPROM are supplied under acceptable terms or independently
   replaced;
4. resident tables and boot/DFU behavior are specified or replaced;
5. exact Apache-2.0 PDL and licensed runtime providers are selected.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 g2/tools/analyze_g2_touch_software_readiness.py --write-manifests --json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest g2.tests.test_analyze_g2_touch_software_readiness
```

The analyzer and its generated manifests are MIT-licensed. The authenticated
official blob is evidence and is not relicensed by this ledger.

# Cordio ATT client-discovery source recovery

Status date: 2026-08-08  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The complete linked `attc_disc.c` translation unit is bounded at
`[0x0056B7EC,0x0056C3B0)`. Fifteen linked functions contribute 2,908 code
bytes; four alignment/literal pools contribute the remaining 104 bytes. The
whole 3,012-byte interval has SHA-256
`d759dc33b12a98e42127bd1551dcd61038d6dfc6551c79b363c970d7f1f3281c`.

Packetcraft r20.05 through r20.05c provides the exact Apache-2.0 public
definition/behavior family. Stock contains the r20-only post-match `break` in
characteristic discovery and its retained line numbers track the r20 layout,
excluding the older AmbiqSuite 2.5.1/r19 implementation.

## Upstream pin and version evidence

AmbiqSuite R2.4.2/R2.5.1 and Packetcraft r19.02 share Git blob
`20961fd7d9cec56a8b8d1e3e165962059275006d`, SHA-256
`b205d964dc1f2d44d540018ee51932c5cf0efdd846018b5b3ff285277621d808`.
Packetcraft r20.05 through r20.05c are invariant for this file:

- selected commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`;
- Git blob `ebb7e5658db198940c6eaaef85ec9a7fbe4f0936`;
- 28,391-byte file, SHA-256
  `04bcbca9aed5610cebd55f160b6c6c658cf0fa01afb276c6caaabe37b55bc91a`.

The retained path at `0x006DC7B4` is
`third_party\cordio\ble-host\sources\stack\att\attc_disc.c`. Stock line
constants 238, 389, 398, 610, 629, and 678 align with the r20 source layout.
The r20-only included-service routines are not linked, but their absence is
consistent with function garbage collection and does not weaken the positive
r20 discriminator in `attcDiscProcCharDecl`.

## Complete stock map

| Function | Stock interval | Bytes |
|---|---:|---:|
| `attcUuidCmp` | `0x56B7EC..0x56B834` | 72 |
| `attcDiscVerify` | `0x56B834..0x56B86A` | 54 |
| `attcDiscDescriptors` | `0x56B86A..0x56B8FA` | 144 |
| `attcDiscProcDescPair` | `0x56B8FA..0x56BA82` | 392 |
| `attcDiscProcDesc` | `0x56BA82..0x56BB1A` | 152 |
| `attcDiscProcCharDecl` | `0x56BB1C..0x56BE24` | 776 |
| `attcDiscProcChar` | `0x56BE30..0x56BEB6` | 134 |
| `attcDiscConfigNext` | `0x56BEB6..0x56BF12` | 92 |
| `AttcDiscService` | `0x56BF12..0x56BF32` | 32 |
| `AttcDiscServiceCmpl` | `0x56BF32..0x56C1B8` | 646 |
| `AttcDiscCharStart` | `0x56C1B8..0x56C1DA` | 34 |
| `AttcDiscCharCmpl` | `0x56C1F8..0x56C34C` | 340 |
| `AttcDiscConfigStart` | `0x56C388..0x56C396` | 14 |
| `AttcDiscConfigCmpl` | `0x56C396..0x56C3A6` | 16 |
| `AttcDiscConfigResume` | `0x56C3A6..0x56C3B0` | 10 |

The body concatenation SHA-256 is
`5327e9fb7478cbf5e9c175d33cf7dfe9b26292344e75a10f45ac767a85853452`.
The exact body/source hashes and all 20 direct BL sites are pinned in
`tools/manifests/packetcraft-cordio-attc-disc-function-map.tsv`. Twelve calls
are internal and eight enter from the product discovery state machine. There
are no indirect calls, stored entry/interior pointers, or exterior branches
into function interiors.

The three r20-only definitions `attcDiscProcIncSvc`,
`AttcDiscIncSvcStart`, and `AttcDiscIncSvcCmpl` are source-only/dead-stripped:
no body, caller, function pointer, or identifying literal remains in stock.

## ABI and state machine

The caller-owned discovery control block is exactly 20 bytes:

```text
+0x00 pCharList       +0x04 pHdlList        +0x08 pCfgList
+0x0C charListLen     +0x0D cfgListLen      +0x0E serviceStart
+0x10 serviceEnd      +0x12 charListIdx      +0x13 endHdlIdx
```

Characteristic and configuration records are each eight bytes. Settings bits
are UUID128 `1`, required `2`, and descriptor `4`. The recovered state machine
parses 4/18-byte descriptor pairs and 7/21-byte characteristic pairs, verifies
required handles, discovers descriptors after characteristic discovery, and
drives read/write configuration one record at a time. Status constants are
`0x0A` not found, `0x73` invalid response, `0x75` undefined, `0x76` required
not found, and `0x79` continuing.

## Lorelei result and reproducibility

The repository owns
`research/readiness/attc-disc/` (6,098 bytes, SHA-256
`4eb7f6e029c8a6cd8395bf0d9a9003b5f61c8870f367b6ef9c43c5b2957af34f`).
Its sixteen inner hashes authenticate the eighteen-function source inventory,
four conservative retained-path anchors / 2,154 bytes, two ARM GCC probes,
eleven provider seams, version evidence, and two zero-unresolved closure
links. Local authenticated binary closure expands the conservative Lorelei map
to all fifteen linked functions / 2,908 bytes.

The artifact excludes firmware, upstream source, decompilation, objects,
ELFs, and caches. Reproduce the fail-closed checks from `openCFW`:

```sh
python3 tools/analyze_g2_cordio_attc_disc.py --json
python3 tools/verify_research_corpus.py --json
```

## Production replacement

`components/shared/cordio/runtime_cordio_attc_disc.c` implements all eighteen
source definitions. Fifteen linked entries use guarded redirects to replace
all 2,908 stock body bytes with 1,610 compiled Cortex-M55 bytes plus 16
alignment bytes under 18 strict relocations. The three included-service
definitions remain source-only/dead-stripped and independently target-compile.

The implementation hardens response-pair shapes and trailing lengths, null
pointers, descriptor-first/index underflow, service-handle ranges,
configuration handle indexes, required-characteristic validation, and
malformed-response cleanup. Host tests cover service, characteristic,
descriptor, included-service, configuration-read/write, and failure paths.

The canonical overlay/component/package identities are 353,336 / 3,876,732 /
4,655,226 bytes with SHA-256 values
`31eec27c1b67e8740a77144c24896a367239d0816fa48acee6b4926b14898106`,
`3aba35b870b09b678b1af07680b2db1ab61962baf0247a6e1b806954a6726444`,
and `b10166d4f1c1f91f348c3ee360afb2af1499df59715491a1256a1d0545f548bc`.
No image was signed, flashed, or installed. Live discovery/configuration,
ATT-peer interoperability, and EM9305 timing remain blocked by unavailable
authorized responsive physical evidence.

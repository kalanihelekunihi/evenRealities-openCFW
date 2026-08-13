# Nanopb iterator-cluster source audit

## Decision

The contiguous G2 range `[0x004D916E,0x004D9522)` is an authenticated
948-byte nanopb `pb_common.c` iterator and default-callback cluster. All eleven
stock functions are bounded and semantically recovered. Nine isolated source
leaves are production-placed: one private descriptor provider and eight live
public/callback entries. Every live stock entry now has a full-span `B.W` plus
Thumb-NOP replacement. The 536 unreachable private stock bytes remain
opaque/cut-forward rather than being overclaimed as source ownership.

## Stock segmentation

The complete cluster SHA-256 is
`067d3a89db02db4ecc9b71e17dc4243c1f61b64ec3c40cfaf90cf07bb1d0b362`.

| Function | Stock span | Bytes | SHA-256 |
|---|---:|---:|---|
| `load_descriptor_values` | `[0x004D916E,0x004D930A)` | 412 | `bdab791c...0c16e` |
| `advance_iterator` | `[0x004D930A,0x004D9384)` | 122 | `435d7c08...d170e` |
| `pb_field_iter_begin` | `[0x004D9384,0x004D93A4)` | 32 | `cc5525b5...c4277` |
| `pb_field_iter_begin_extension` | `[0x004D93A4,0x004D93D8)` | 52 | `fee54683...2026` |
| `pb_field_iter_next` | `[0x004D93D8,0x004D93F8)` | 32 | `fd4a8582...71f7` |
| `pb_field_iter_find` | `[0x004D93F8,0x004D946E)` | 118 | `08bc6b10...8005` |
| `pb_field_iter_find_extension` | `[0x004D946E,0x004D94B8)` | 74 | `6551f777...7bde` |
| `pb_const_cast` | `[0x004D94B8,0x004D94BA)` | 2 | `c7dfbb7d...8df8` |
| `pb_field_iter_begin_const` | `[0x004D94BA,0x004D94D2)` | 24 | `1d71a069...4827` |
| `pb_field_iter_begin_extension_const` | `[0x004D94D2,0x004D94E6)` | 20 | `f67d2e9c...758e` |
| `pb_default_field_callback` | `[0x004D94E6,0x004D9522)` | 60 | `1ec35a15...3d03` |

The analyzer pins every direct caller and all sixteen fixed calls. Fifteen
calls are internal to the cluster. The only external fixed call is the
released memory-fill routine at `0x0043C0E4`; the source implementation replaces it
with a private byte loop. The default callback has two authenticated indirect
`BLX r3` application/schema callback sites and no fixed callback target.

One apparent narrow branch from `0x004D9118` into `0x004D9174` is inside the
66-byte literal/data island `[0x004D910A,0x004D914C)`, not executable ingress.
The island is hash-pinned. The sole stored pointer is the legitimate Thumb
pointer `0x004D94E7` at `0x004910BC`, selecting
`pb_default_field_callback`. No unclassified alternate or interior ingress
remains.

## Upstream identity and corrected release range

The selected source oracle remains nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. The exact upstream definition
cluster is `pb_common.c[145:10196]`, 10,051 bytes with SHA-256
`cfd4ae8e8dac527ba9332809e3038c101199a26d271fd51ae0bc154c927469e8`.
The entire 12,141-byte `pb_common.c` file has SHA-256
`8d2ec28baaaf2b7a5e90e4cb2fa9700d21cef7f826f051a637c30b7a1e6a0516`
at every official release from 0.4.4 through 0.4.9.1. This component alone
does not discriminate the release.

The broader stock runtime still excludes pristine 0.4.4--0.4.6 through the
`pb_read` lower-bound discriminator. A new upstream lookup found 0.4.9.1
commit `cad3c18ef15a663e30e3e43e3a752b66378adec1`. Its sole runtime behavior
change from 0.4.9 is in `pb_decode_ex`, which is dead-stripped in G2. The
firmware timestamp `2025-04-28T13:29:15Z` postdates its 2024-12-01 release.
The defensible pristine candidate range is therefore 0.4.7--0.4.9.1, while
0.4.9 remains openCFW's deliberate authenticated compatibility baseline.

## Production source and placement

The production files are:

- `components/shared/nanopb/runtime_nanopb_iterator_cluster.c`, 13,395 bytes,
  SHA-256 `edcff9480ae181a22aba9eb28641257fe62fb9652c1268cd3ef1658e5a3690eb`;
- `components/shared/nanopb/runtime_nanopb_iterator_cluster.h`, 2,995 bytes,
  SHA-256 `f9664d9eb409a731dbf1a7c664ee91f10b58b3b0f818844eab5f77fbaac8f0b2`.

Apple Clang 21.0.0 with the production Thumb flags emits a 4,564-byte object,
SHA-256 `b4049aec70c47ed1b617661d44fc400894e409f00bf472af19b34a0ff69d2ebc`.
It has eight public text sections plus one private
`open_cfw_nanopb_load_descriptor_values` section and no undefined symbol.
The compiler inlines `advance_iterator`, `pb_const_cast`, and the begin logic
where profitable. Host tests cover mixed one-/two-word descriptors, iterator
advance/wrap, backward find, extension discovery, null messages, and dynamic
callback dispatch.

Source identification, source recreation, and reviewed target compilation are
estimated 100% complete. Production entry routing, relocation/placement review,
manifest changes, and ownership transfer are also 100% complete for the eight
live entries. The integration closes six decoder/defaults call sites across
five unique iterator entries. Calls that still name stock entry addresses now
land only on authenticated generated redirects; no retained stock executable
body or fixed stock-data seam remains in the live closure.

| Overlay leaf | Address | Bytes |
|---|---:|---:|
| private descriptor provider | `0x007B33B8` | 238 |
| `pb_field_iter_begin` | `0x007B34A8` | 90 |
| `pb_field_iter_begin_extension` | `0x007B3504` | 128 |
| `pb_field_iter_next` | `0x007B3584` | 94 |
| `pb_field_iter_find` | `0x007B35E4` | 172 |
| `pb_field_iter_find_extension` | `0x007B3690` | 140 |
| `pb_field_iter_begin_const` | `0x007B371C` | 90 |
| `pb_field_iter_begin_extension_const` | `0x007B3778` | 128 |
| `pb_default_field_callback` | `0x007B37F8` | 52 |

The isolated selector builds contribute 1,132 source bytes and 10 alignment
bytes. Eight entry replacements transfer 412 stock bytes from opaque to
generated ownership. Package ownership is therefore 129,014 source bytes
(2.912179%), 90,977 generated bytes (2.053585%), and 4,210,163 opaque bytes
(95.034236%). The Apple overlay/component/package pins are respectively
128,264 / 3,651,660 / 4,430,154 bytes with SHA-256
`742e44dd839010c3c14ae59419fc06bcd50a7fe91e7ba06b4946f5c4154c870b`,
`ea39a91f574b464d9071e581f5104d870e1f7e484d52de9b86407f0a90ac5d2e`,
and `aa71330ceed2775494fb7ff599a23701ef746a25452a8d335574a3bac12674a9`.

## Independent reverse engineering

Rizin recovered all eleven boundaries and calls. The updated Ghidra helper
accepted seven addresses in one noanalysis import and decompiled the complete
descriptor load, iterator advance, begin, begin-extension, next, find, and
find-extension control flow in 6.3 seconds. It independently confirmed the
16-bit iterator counters, one-byte type field, compact 1/2/4/8-word descriptor
formats, pointer indirection, fixed-count `array_size` alias, and submessage
descriptor indexing.

## Reproduction

```sh
python3 tools/analyze_g2_nanopb_iterator_cluster.py --json
python3 -m unittest \
  tests.test_analyze_g2_nanopb_iterator_cluster \
  tests.test_runtime_nanopb_iterator_cluster
```

These checks are offline and perform no signing, flashing, reset, or hardware
operation. Linux placement and hardware execution remain deferred.

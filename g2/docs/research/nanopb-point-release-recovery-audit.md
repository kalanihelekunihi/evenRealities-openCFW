# nanopb Point-Release Recovery Audit — G2 Apollo-main

**Status: exact point release unresolved; pristine-upstream candidate set narrowed to
0.4.7–0.4.9.1.** This is a read-only provenance audit. It does not alter production
manifests, overlays, firmware, or hardware.

## Result

The authenticated G2 `g2-2.2.6.10` Apollo-main image contains a release-discriminating
`pb_read()` behavior introduced by official nanopb 0.4.7. This excludes pristine
0.4.4, 0.4.5, and 0.4.6 reference sources. It does **not** distinguish 0.4.7 from
0.4.8, 0.4.9, or 0.4.9.1:

| Candidate | Pristine official runtime result | Reason |
|---|---:|---|
| 0.4.4 | excluded | lacks both later discriminators |
| 0.4.5 | excluded | lacks both later discriminators |
| 0.4.6 | excluded | has the 63-bit varint guard, but lacks the `pb_read()` saturating clamp |
| 0.4.7 | survives | has both observed instruction behaviors |
| 0.4.8 | survives | runtime C is behaviorally identical to 0.4.7 for this target/configuration |
| 0.4.9 | survives | its type/annotation edits preprocess identically for this target/configuration |
| 0.4.9.1 | survives | its sole runtime behavior change is in dead-stripped `pb_decode_ex` |

The lower-bound wording is deliberately qualified: a vendor backport can make an older
release produce either behavior. In the absence of a source manifest or embedded version
stamp, the defensible claim is **“compatible with unmodified upstream 0.4.7–0.4.9.1,”**
not an unequivocal exact version.

## Authenticated firmware evidence

| Item | Pin |
|---|---|
| Image | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Size | 3,523,396 bytes |
| SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Mapping | `run_addr = file_offset + 0x00437FE0` |
| nanopb window | `0x0048F000–0x00491400`, SHA-256 `ff42ff15a4574a6485b8b3e16de986679f059f2358d5d354b29f713760f43ea2` |
| `pb_read` | `0x0048F3BE–0x0048F454`, SHA-256 `69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f` |
| `pb_decode_varint` | `0x0048F5B8–0x0048F628`, SHA-256 `f93d678981f92603982c9afc6c6f9976ca14d1a7a7e0bfc949d3ff73f2791ff2` |

At `0x0048F43C`, the unique Thumb sequence performs:

```c
if (stream->bytes_left < count)
    stream->bytes_left = 0;
else
    stream->bytes_left -= count;
```

That exact source branch was added between the official `nanopb-0.4.6` and
`nanopb-0.4.7` tags. The preceding callback can adjust `bytes_left`, which is why this
second test exists. The G2 instructions are `ldr; cmp; bhs; movs #0; str; b; ldr; subs;
str`, and the complete 18-byte sequence occurs once, at the expected address.

At `0x0048F5D4`, a second unique sequence implements the 64-bit varint condition
`bitpos >= 63 && (byte & 0xFE) != 0`. Official history places this change in 0.4.6.
This corrects the earlier `nanopb-recovery-audit.md` attribution to 0.4.4; it
corroborates the later lower bound but does not distinguish the surviving releases.

No `nanopb-0.4.4` through `nanopb-0.4.9.1` string occurs in the image. `NANOPB_VERSION`
is a preprocessor macro and is not emitted unless application code references it.

The unique firmware build timestamp is `2025-04-28T13:29:15Z` at
`0x00768290`, after the 0.4.9.1 release. Between 0.4.9 and 0.4.9.1, the only
runtime C change makes `pb_decode_ex` preserve a close-substream failure in
`status` rather than return immediately. Stock has no retained `pb_decode_ex`:
the complete direct-call topology for `pb_make_string_substream`,
`pb_close_string_substream`, and `pb_decode_inner` contains only the already
identified static-field, pointer-field, public `pb_decode`, and private
submessage paths. Therefore this source change cannot discriminate the image.

## Official upstream identities

Repository: `https://github.com/nanopb/nanopb.git`. License: **Zlib**, identical
`LICENSE.txt` SHA-256 in all seven tags:
`e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d`.

| Tag | Commit | Tree | Date |
|---|---|---|---|
| `nanopb-0.4.4` | `2b48a361786dfb1f63d229840217a93aae064667` | `5483fd3823bda3c30671d85a8919633f98309e1e` | 2020-11-25 |
| `nanopb-0.4.5` | `c9124132a604047d0ef97a09c0e99cd9bed2c818` | `27e977c6c2e809a42fa07692e72d6f3dbfee78d0` | 2021-03-22 |
| `nanopb-0.4.6` | `afc499f9a410fc9bbf6c9c48cdd8d8b199d49eb4` | `a0e54e9fe89eb1b42ee0931bec5d39570efc6ed7` | 2022-05-30 |
| `nanopb-0.4.7` | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `2eb286236013d6d82f12383aa0e6fa316a78172e` | 2022-12-11 |
| `nanopb-0.4.8` | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `0197a003666f5fd44eb73d565aabe24ef8e11543` | 2023-11-11 |
| `nanopb-0.4.9` | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `2c4c260bcff3f9f7081238d377274dd385d76582` | 2024-09-19 |
| `nanopb-0.4.9.1` | `cad3c18ef15a663e30e3e43e3a752b66378adec1` | `2962227caf93b83e9fd67d5d17b96fc498648dea` | 2024-12-01 |

The analyzer pins SHA-256 identities for `pb.h`, `pb_common.c/.h`, `pb_decode.c/.h`,
`pb_encode.c/.h`, and `LICENSE.txt` in every tag. With `--upstream-repo`, it verifies
all commits, trees, and files without trusting the checkout's working tree.

## Reference builds and why exact recovery stops here

Each tag was compiled from its authenticated Git object content with:

```text
clang -target arm-none-eabi -mcpu=cortex-m55 -mthumb -Os
      -ffunction-sections -fdata-sections -fno-ident
      -ffreestanding -fno-builtin
```

The recovered G2 configuration uses the nanopb defaults relevant to this comparison:
malloc off, 16-bit `pb_size_t`, 64-bit values enabled, and UTF-8 validation off. The
builds are not claimed as byte matches for the shipped IAR image; they are a controlled
test of whether pristine candidates remain distinguishable after compilation.

Under Apple Clang 21.0.0 (`clang-2100.3.27.1`), the object SHA-256 triplet order is
`pb_common.o`, `pb_decode.o`, `pb_encode.o`:

| Release | Object SHA-256 triplet (abbreviated) |
|---|---|
| 0.4.6 | `8e4be109…`, `534518b8…`, `1b8296fe…` |
| 0.4.7 | `8e4be109…`, `bd829ad3…`, `1b8296fe…` |
| 0.4.8 | `8e4be109…`, `bd829ad3…`, `1b8296fe…` |
| 0.4.9 | `8e4be109…`, `bd829ad3…`, `1b8296fe…` |
| 0.4.9.1 | `8e4be109…`, `62dc1eac…`, `1b8296fe…` |

The analyzer contains the complete hashes and can rerun this proof using
`--reference-build`. Releases 0.4.7 through 0.4.9 produce byte-identical
complete runtime object triplets. Release 0.4.9.1 has identical `pb_common.o`
and `pb_encode.o`; only `pb_decode.o` changes because it contains the
dead-stripped `pb_decode_ex` section. This is expected:

- 0.4.7 → 0.4.8 changes only the version macro and C++/MSVC header behavior, neither
  retained in these C runtime objects.
- 0.4.8 → 0.4.9 moves `pb_byte_t`, changes header comments, and enables a return-value
  annotation for newer IAR; on an 8-bit-byte ARM target the effective C/runtime is the
  same, and the annotation does not emit code.
- 0.4.9 → 0.4.9.1 changes the version macro and `pb_decode_ex`; neither
  discriminator is retained in G2.

Consequently, a same-compiler byte comparison against the G2 runtime cannot choose among
0.4.7, 0.4.8, 0.4.9, and 0.4.9.1. Selecting one would be guesswork.

## Reproduction

Binary-only, offline audit:

```sh
python3 tools/analyze_g2_nanopb_point_release.py --pretty
python3 -m unittest -v tests.test_analyze_g2_nanopb_point_release
```

Authenticate official upstream Git objects and reproduce the build collision:

```sh
git clone --filter=blob:none --no-checkout https://github.com/nanopb/nanopb.git /tmp/nanopb
python3 tools/analyze_g2_nanopb_point_release.py \
  --upstream-repo /tmp/nanopb --reference-build --pretty
```

## What would resolve the remaining ambiguity

One of these external artifacts is required:

1. a vendor dependency manifest, SBOM, submodule SHA, package lock, or build log;
2. generated `.pb.c/.pb.h` source with its nanopb generator-version comment;
3. a referenced application string produced from `NANOPB_VERSION`; or
4. a known `.proto` schema whose generated descriptors differ between the candidate
   generators and can be matched uniquely to retained descriptor bytes.

Until one is recovered, source adoption should pin a reviewed candidate deliberately and
record it as a compatibility choice, not mislabel it as the uniquely identified vendor
point release.

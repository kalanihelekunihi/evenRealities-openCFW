# littlefs `lfs_tag_chunk` production source audit

Date: 2026-08-02

Scope: authenticate the private littlefs `lfs_tag_chunk` leaf in both official
G2 firmware images and atomically integrate a shared source adaptation into
the Apollo-main and bootloader production overlays.

Decision: **GO for atomic dual-image production source integration and normal
offline firmware assembly; NO-GO for signing or hardware flashing.**

The Apollo-main body at `[0x004CAEA0,0x004CAEA6)` and bootloader body at
`[0x00410BA8,0x00410BAE)` are byte-identical, call-free six-byte Thumb leaves.
Each image has exactly four decoded direct calls to its entry and no observed
alternate or interior ingress from any audited branch or stored-pointer class.
The production adapter implements the exact scalar behavior of the
authenticated littlefs v2.10.1 definition. It is registered in both overlay
registries, the canonical source manifest, and bounded littlefs provenance.

No firmware artifact was changed, built for release, signed, flashed, booted,
or exercised on G2 hardware for this audit.

## Authenticated upstream definition

| Property | Pin |
|---|---|
| Repository | `https://github.com/littlefs-project/littlefs.git` |
| Selected release | `v2.10.1` |
| Selected commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| License | BSD-3-Clause |
| `third_party/littlefs/lfs.c` | 196,753 bytes; SHA-256 `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |

The exact upstream definition is `lfs.c` bytes `[10514,10607)`, 93 bytes,
SHA-256
`406b74c2d10482c959cf1048d9589d00d8b416ee4661203bd339144baa74cd09`:

```c
static inline uint8_t lfs_tag_chunk(lfs_tag_t tag) {
    return (tag & 0x0ff00000) >> 20;
}
```

The selected slice includes the two newlines after the closing brace. The
private type declaration is exactly `typedef uint32_t lfs_tag_t;`, `lfs.c`
bytes `[9602,9629)`, 27 bytes, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
The recovered contract is therefore a pure unsigned 32-bit mask and shift
whose result is in `[0,255]` and fits exactly in `uint8_t`.

The selected tree is an authenticated source-equivalent baseline; the
stripped images do not prove it was Even Realities' exact historical checkout.
`third_party/littlefs/PROVENANCE.json` retains that ambiguity. The local source
and header preserve the upstream copyright notices and BSD-3-Clause SPDX
identifier.

## Authoritative firmware inputs and stock bodies

| Input | Bytes | SHA-256 |
|---|---:|---|
| Official Apollo-main OTA `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Apollo-main installed payload after the 32-byte OTA preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Official bootloader `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

Apollo main loads at `0x00438000`. Its stock body begins at installed
payload offset `0x00092EA0` and OTA file offset `0x00092EC0`. The bootloader
loads at `0x00410000`, placing its stock body at file offset `0x00000BA8`.

| Image | Runtime span | Bytes | SHA-256 |
|---|---|---|---|
| Apollo main | `[0x004CAEA0,0x004CAEA6)` | `000dc0b27047` | `63fc572597119c756fa5d4ee0904c8c34dfa545495b77bba02e2ff3298ce23ae` |
| Bootloader | `[0x00410BA8,0x00410BAE)` | `000dc0b27047` | `63fc572597119c756fa5d4ee0904c8c34dfa545495b77bba02e2ff3298ce23ae` |

The Thumb body shifts `r0` right by 20 bits, applies an 8-bit truncation, and
returns through `lr`. This is algebraically identical for unsigned `uint32_t`
input to upstream `(tag & 0x0ff00000) >> 20`. No decoded outgoing branch is
present in either body.

## Exact callers and complete-image ingress closure

The complete Apollo-main payload has exactly these direct `BL` entries:

| Call site | Encoding | Target |
|---:|---|---:|
| `0x004CAEA8` | `fff7faff` | `0x004CAEA0` |
| `0x004CBB68` | `fff79af9` | `0x004CAEA0` |
| `0x004CBD1E` | `fff7bff8` | `0x004CAEA0` |
| `0x004CCBC4` | `fef76cf9` | `0x004CAEA0` |

| Apollo-main evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `53fe680d2304be812e2d3d7b4c194642f0250aacddfa2a2d319dcb9c04a77a20` |
| concatenated encodings | `089750335e98afdca16b29120336a01172cdc3c7584094cd5c2952ef885cc742` |
| address-plus-encoding records | `4d34c3705c5ada46756ea6ffcf00722a1d960716627d0f293ea6bf03b9b655b0` |

The complete bootloader has exactly these direct `BL` entries:

| Call site | Encoding | Target |
|---:|---|---:|
| `0x00410BB0` | `fff7faff` | `0x00410BA8` |
| `0x00411870` | `fff79af9` | `0x00410BA8` |
| `0x00411A26` | `fff7bff8` | `0x00410BA8` |
| `0x004127C8` | `fef7eef9` | `0x00410BA8` |

| Bootloader evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `0d397f7452143ad98aff7e29880f28885c35d8ab24b1481e057dabff3a1e478f` |
| concatenated encodings | `077793ca6848ed5f3c7fabf50d9698fb2ef23ef3010e99fa3fa854aee5d28ff3` |
| address-plus-encoding records | `b74dadb016ec167ffc6aadae7ff6bdbb6120671cfcbaa239682f13ad6a45b97a` |

For both images, a halfword-aligned scan through the final complete halfword
found exactly the four listed `BL` entries and found no `B.W`, wide
conditional, narrow unconditional, narrow conditional, `CBZ`, or `CBNZ`
entry into the body. It found no external branch to an interior halfword and
no byte-aligned stored even or Thumb address for any byte address in either
span. These checks close the decoded branch and stored-address classes used by
the focused gate; they are not a universal data-flow proof against an address
synthesized by an unrecognized multi-instruction sequence.

## Scalar ABI and source differential

The isolated callable contract is AAPCS32 Thumb, little-endian:

| Register | Meaning |
|---|---|
| `r0` on entry | one unsigned 32-bit `lfs_tag_t` value |
| `r0` on return | zero-extended unsigned 8-bit chunk value |

There are no pointer or stack arguments, structure layouts, providers, global
state, allocation, filesystem-object access, callback, or hardware dependency.
The production header exposes only a `uint32_t` scalar alias and a `uint8_t`
result, with compile-time width assertions.

The focused differential compiles the actual authenticated upstream definition
beside the production adapter and compares both through those scalar types. It checks
eight directed edge and pattern values, exhausts all 4,096 combinations of
source-relevant bits 20 through 31 with deterministic lower-bit noise, and
checks 20,000 seeded random 32-bit inputs. All 24,104 comparisons match the
pristine definition; the exhaustive portion covers every combination of bits
that can affect the result.

## Deterministic Apple target object closure

Apple Clang `21.0.0 (clang-2100.3.27.1)` compiles the production adapter twice for
`thumbv7em-none-eabi` at `-O2` with the focused freestanding and deterministic
flags. Both output objects are byte-identical:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| target ELF object | 784 | `517b3e244b391c21f714f21c54544b9ce93a6008781e2daa536e3f954ddf2f9d` |
| `.text.open_cfw_littlefs_tag_chunk` | 6 | `db1dfda72afb267e96cd4e11eaf5d44659195b0afecbdcd8ed8572c34049df74` |

The complete isolated text is `c0f307507047`, aligned to four bytes. It has
zero undefined symbols and zero text relocations. The only other allocated
section is the canonical eight-byte
`.ARM.exidx.text.open_cfw_littlefs_tag_chunk` record (flags `130`), which the
focused extractor authenticates and discards. This closes the generated
function's provider and relocation dependencies.

## Production artifacts and registration gate

| Production input | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/littlefs/runtime_littlefs_tag_chunk.c` | 773 | `71851bd05e26e703b8697b9994b556db46511c37e9500da98e3406b37a92c8da` |
| `components/shared/littlefs/runtime_littlefs_tag_chunk.h` | 879 | `1061f5d68ff6f81a6f1853bfefe37b77f5f3b8b09e627b1bfa0d191842d1f6f5` |

The focused test pins both source files, the pristine upstream bytes, official
image identities, both stock bodies, both caller sets, object bytes, extracted
text, and relocation closure. It requires the source path, header path, and
symbol to be registered exactly in:

- `components/apollo_main/core_overlay/overlay.json`;
- `components/bootloader/core_overlay/overlay.json`;
- `manifests/g2-2.2.6.10-core-source.json`; and
- `third_party/littlefs/PROVENANCE.json`.

Both stock bodies are replaced by authenticated six-byte `B.W` entry patches.
The compiled source leaf is placed at Apollo-main overlay offset `124560`
(`0x007B29B4`) for Apple and `126380` (`0x007B30D0`) for Linux. The bootloader
leaf is at offset `622` (`0x004346E6`) under both profiles. Current aggregate
pins include the subsequent atomic `lfs_tag_isvalid` / `lfs_tag_type1`
promotion. Apple Apollo main is `3,647,982` bytes, SHA-256
`1227c4953bfcaeb62fb497b8a6911462a2d25fd3ed7b2bb88eea9dd3fdf13a18`;
bootloader is `149,244` bytes, SHA-256
`e8924fe19f6f768d01fa7c6ec111a4db5790eb28c423c5be84e09b0996423e20`;
and the package is `4,426,458` bytes, SHA-256
`f0e7e4c5e090ea558968b6293f3eec0a7f88a6126ea164547c25c8462b60be23`.
The corresponding exact-root Linux Apollo-main component is `3,649,802`
bytes, SHA-256
`a8684ae43a99cc692dd6cb95c8d4835cc138492d49bf9fd4a3689d32523913ef`;
the Linux bootloader is `149,244` bytes, SHA-256
`6fff06068442ab3203d124c0adfd5052f216459642f67aa32cc39afffd2c0593`;
and the Linux package is `4,428,278` bytes, SHA-256
`07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc`.

The manifest records exact source, generated-entry, alignment, and official
blob regions contiguously across each component. No build in this audit signs,
transmits, flashes, erases, resets, or otherwise communicates with hardware.

## Reproduction

```sh
python3 -m py_compile tests/test_runtime_littlefs_tag_chunk.py
python3 -m unittest -v tests.test_runtime_littlefs_tag_chunk
git diff --check -- components/shared/littlefs/runtime_littlefs_tag_chunk.c components/shared/littlefs/runtime_littlefs_tag_chunk.h tests/test_runtime_littlefs_tag_chunk.py docs/research/littlefs-tag-chunk-candidate-audit.md
```

Expected focused result: five tests pass. Temporary compiler products are
created only under `build/` and removed by the test harness.

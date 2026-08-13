# littlefs `lfs_file_rewind_` production source audit

Date: 2026-08-02

Scope: the private Apollo-main `lfs_file_rewind_` leaf in official G2 firmware
`2.2.6.10`, its bounded openCFW source replacement, and the recorded Apple
Clang and Linux Clang build profiles.

Decision: **GO (high confidence), limited to the authenticated source
replacement and reproducible build/package boundary described here.**

The 18-byte stock routine at `[0x004CE460,0x004CE472)` is a complete private
littlefs leaf with one entry caller and one outgoing provider. Its behavior is
exactly the behavior of `lfs_file_rewind_` in the authenticated littlefs
v2.10.1 source-equivalent snapshot: call private `lfs_file_seek_` with offset
zero and `LFS_SEEK_SET`, preserve a negative result, and normalize every
nonnegative result to zero. The production source adaptation preserves that
contract while leaving its two pointer types opaque.

This GO does **not** claim that the selected Git commit was Even Realities'
exact historical checkout, that the retained `lfs_file_seek_` provider is now
source-owned, or that the resulting image has been signed, flashed, booted, or
validated on G2 hardware. It does not authorize filesystem format, migration,
erase, or any other mutating hardware experiment.

## Authenticated upstream and license

The selected snapshot is:

| Property | Pin |
|---|---|
| Repository | `https://github.com/littlefs-project/littlefs.git` |
| Selected release | `v2.10.1` |
| Commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| Tree | `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` |
| Commit date | `2024-12-20T09:02:13-06:00` |
| License | BSD-3-Clause |
| `lfs.c` | 196,753 bytes; SHA-256 `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `LICENSE.md` | 1,523 bytes; SHA-256 `0cb4ff1daf5fdc1359c6a6ee3116092f08fc100c9d58b1b77ab17bfd801f856d` |

The license and the local adaptation retain copyright attribution to the
littlefs authors (2022) and Arm Limited (2017) and use the SPDX identifier
`BSD-3-Clause`.

The repository classifies this as a **source-equivalent release baseline**.
The complete 38-assertion bootloader line fingerprint selects v2.10.1 among
the 38 inspected official v2 tags, and Apollo main has the same source
generation. This is strong behavioral/source authentication, but it cannot
prove the vendor's precise historical repository state. In particular, the
selected `lfs.c` state and two later upstream source states compile
byte-identically with the recovered G2 configuration: one later state adds an
explicit cast and another differs only in disabled trace code. That
binary-equivalence ambiguity is deliberately retained in
`third_party/littlefs/PROVENANCE.json` rather than being resolved by
assumption.

## Exact upstream contract

The authenticated definition is at `lfs.c` lines 3841-3849, byte span
`[118157,118349)`, length 192, SHA-256
`74638292061613417c2ce7c6bbed200d2bee046c35a7a835fb4d9bb183ab755a`:

```c
static int lfs_file_rewind_(lfs_t *lfs, lfs_file_t *file) {
    lfs_soff_t res = lfs_file_seek_(lfs, file, 0, LFS_SEEK_SET);
    if (res < 0) {
        return (int)res;
    }

    return 0;
}
```

Its complete semantic contract is therefore:

1. Forward `lfs` and `file` unchanged to `lfs_file_seek_`.
2. Pass a signed offset of exactly zero and `LFS_SEEK_SET == 0`.
3. Call the provider exactly once.
4. If the signed 32-bit provider result is negative, return that exact value.
5. If the provider result is zero or positive, return zero.

No `lfs_t` or `lfs_file_t` field is read directly by this leaf. The filesystem
and file structures can consequently remain incomplete types at this
boundary; their layout belongs to the retained seek provider, not to the
replacement.

## Authoritative stock image and bytes

| Input | Bytes | SHA-256 |
|---|---:|---|
| Official OTA package `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed Apollo application after the 32-byte OTA preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Official bootloader `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

The installed application load address is `0x00438000`. The private rewind
body begins at installed payload offset `0x00096460` and OTA file offset
`0x00096480` (`615552` decimal).

The complete stock function is:

```text
span    [0x004CE460,0x004CE472)
size    18 bytes
bytes   80b500230022fff7a9ff002800d4002002bd
sha256  be02691b2e7339d7dd1d54b31712c3e8563e5a86f4406a469888640fad9435cd
```

Thumb disassembly:

```text
004ce460  80b5       push  {r7, lr}
004ce462  0023       movs  r3, #0
004ce464  0022       movs  r2, #0
004ce466  fff7a9ff   bl    0x004ce3bc
004ce46a  0028       cmp   r0, #0
004ce46c  00d4       bmi   0x004ce470
004ce46e  0020       movs  r0, #0
004ce470  02bd       pop   {r1, pc}
```

The bytes occur once in the Apollo OTA and zero times in the official
bootloader, so this audit authorizes an Apollo-main replacement only.

## Boundary and topology closure

The adjacent stock functions terminate exactly at the proposed boundaries:

| Role | Span | Bytes | SHA-256 |
|---|---|---:|---|
| predecessor tail, private `lfs_file_tell_` | `[0x004CE45C,0x004CE460)` | 4 | `efdc6e5a708e49cc1158aec6dfbde6a0115558c29a0f8c6a6ba9c4075df0fb5f` |
| replacement, private `lfs_file_rewind_` | `[0x004CE460,0x004CE472)` | 18 | `be02691b2e7339d7dd1d54b31712c3e8563e5a86f4406a469888640fad9435cd` |
| successor, private `lfs_file_size_` | `[0x004CE472,0x004CE48A)` | 24 | `98ba58dac7de35e47c75240c0671b11e6b403a1bffed50a617c6543eb26a83cc` |

The predecessor bytes are `486b7047`, an independent load-and-return tail.
The successor bytes are
`80b50800016b890304d5c16a406bfcf73af900e0c06a02bd` and begin with their
own prologue. There is no shared tail, cross-boundary fallthrough, or literal
pool in the 18-byte rewind span.

The private rewind entry has exactly one direct caller:

| Caller | Call site | Encoding | Target |
|---|---:|---|---:|
| public `lfs_file_rewind` wrapper | `0x004CFC28` | `fef71afc` | `0x004CE460` |

The wrapper itself is independently bounded at `[0x004CFC24,0x004CFC2E)`,
10 bytes, bytes `80b50022fef71afc02bd`, SHA-256
`db0377b209a419d889a90e4584af9a0f351ff7f42b192afd90624def52231b46`.
It has one direct caller at `0x0047635C`, encoding `59f062fc`.

A halfword-aligned scan of the complete installed application found, for both
the private leaf and its public wrapper:

- exactly the direct `BL` entry listed above;
- no `B.W` entry;
- no wide conditional, narrow unconditional, narrow conditional, `CBZ`, or
  `CBNZ` entry;
- no external direct branch to an interior halfword; and
- no byte-aligned stored even or Thumb address into the entry or interior.

The scan covers those decoded branch and stored-address classes. It is not a
general whole-program data-flow proof and does not separately prove the
absence of a dynamically computed `MOVW`/`MOVT` target. The unique public
wrapper call plus the absence of any observed alternate ingress is sufficient
for this bounded entry replacement; the limitation remains explicit.

## Sole retained provider

The leaf has one outgoing edge:

| Call site | Encoding | Provider | Provider span | Bytes / SHA-256 |
|---:|---|---|---|---|
| `0x004CE466` | `fff7a9ff` | private `lfs_file_seek_` at `0x004CE3BC` | `[0x004CE3BC,0x004CE45C)` | 160 / `368a3e58188f71ad37233eaca687cd3939a9f06406702a176f9731f22bcaf61f` |

The production leaf represents this edge as the undefined symbol
`open_cfw_littlefs_file_seek_private` and binds it, under a strict relocation
contract, to `0x004CE3BC`. No other official routine, local runtime symbol,
global object, literal, or storage callback is a direct dependency of the
leaf.

This provider remains official binary code. Replacing the 18-byte rewind leaf
therefore advances source ownership without claiming that rewind's complete
transitive implementation is source-owned. A later source recreation of
`lfs_file_seek_` can replace the seam after its larger call graph, file-state
mutations, and configuration-sensitive behavior are independently closed.

## ABI and generated-object closure

The callable ABI is AAPCS32/Thumb, little-endian:

| Register | Meaning |
|---|---|
| `r0` on entry | opaque `lfs_t *` |
| `r1` on entry | opaque `lfs_file_t *` |
| `r2` at provider call | signed `lfs_soff_t` offset, zero |
| `r3` at provider call | `LFS_SEEK_SET`, zero |
| `r0` on return | 32-bit `int`: exact negative provider result, otherwise zero |

The local header asserts 32-bit `int`, 32-bit `lfs_soff_t`,
`LFS_SEEK_SET == 0`, and, on Arm, 32-bit pointers. It intentionally declares
only opaque filesystem/file types and the single provider prototype.

The reviewed target is `thumbv7em-none-eabi`, compiled as Thumb at `-O2` with
freestanding, no-builtin, no-unwind, no-jump-table, ROPI, function/data-section,
warning-as-error, and deterministic-ident flags pinned in `overlay.json`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 produce the same authenticated
object and unrelocated function text:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| target ELF object | 960 | `c7398babd0a9adba9ea4a81c8221d8826f1aac166bebbee4307280778a1443bf` |
| unrelocated `.text.open_cfw_littlefs_file_rewind_private` | 16 | `46e8bab056ad39ced45edb5da2612f6470674ab5a428df7f08822f6c2d9e184b` |

Unrelocated text:

```text
80b500220023fff7feff00eae07080bd
```

There is exactly one relocation and exactly one undefined symbol:

```text
offset       6
type/id      R_ARM_THM_CALL / 10
symbol       open_cfw_littlefs_file_seek_private
symbol type  STT_NOTYPE
target       0x004CE3BC
```

The only allocated object sections are the 16-byte function text and its
8-byte CANTUNWIND `.ARM.exidx` metadata. The extractor authenticates and
discards that metadata. There is no allocated rodata, writable data, second
function, or second runtime seam.

After Apple-profile relocation, the 16-byte leaf is:

```text
80b5002200231bf527fd00eae07080bd
```

The call at `0x007B296A` resolves to `0x004CE3BC`. The final `and.w r0, r0,
r0, asr #31` implements the exact normalization compactly: a negative `r0`
is preserved and a zero or positive `r0` becomes zero.

## Local source authentication and differential behavior

| Local input | Bytes | SHA-256 |
|---|---:|---|
| `components/apollo_main/core_overlay/runtime_littlefs_file_rewind_private.c` | 1,239 | `e6afb5b67671b3219971b19c20290c601568752d814064147f5ccd4118f5acc8` |
| `components/apollo_main/core_overlay/runtime_littlefs_file_rewind_private.h` | 1,743 | `7430dcd1ad1ea3973d619f2d67d8d8b11a688018d48a3bc26a40e407d1fedb56` |

The C file is an explicitly altered, freestanding BSD-3-Clause adaptation,
not a claim of byte-for-byte upstream source identity. It has no allocator,
global state, struct dereference, block-device call, or hardware access.

The focused gate compiles the local source against a provider stub and compiles
the exact 192-byte pristine upstream definition against an equivalent
`lfs_file_seek_` stub. It differentially compares:

- the signed 32-bit extrema and representative negative, zero, and positive
  edge values; and
- 1,000 deterministic random signed 32-bit provider results, with independently
  varied pointer values.

All 1,010 cases require identical local/upstream return values, unchanged
pointer forwarding, offset zero, whence zero, and exactly one provider call.

## Production overlay and entry replacement

`overlay.json` registers the function once, one relocated leaf, and one patch
site. Its current aggregate cardinalities are 647 functions, 596 patch sites,
and 78 relocated leaves. The entry patch authenticates the complete original
18-byte stock span before writing a profile-specific four-byte `B.W` followed
by seven Thumb NOPs.

| Profile | Leaf offset | Runtime | Relocated leaf SHA-256 | Entry replacement bytes | Replacement SHA-256 |
|---|---:|---:|---|---|---|
| Apple Clang 21.0.0 | 124,480 | `0x007B2964` | `1c2e2b1fded0de515345b90fe34de51a9c0f08a02a5ad983c1120481c51c5783` | `e4f280ba` + seven `00bf` | `d6d0947d5f648f4acdab371be5d051e3c89ad1f2e44b88da2ce0600e7b2f3751` |
| Linux Clang 22.1.8 | 126,300 | `0x007B3080` | `9731cbf3ff15be31186591ed148d009ae8985cb18bdfca3ba365aeb0897e3fd1` | `e4f20ebe` + seven `00bf` | `f014878435e10f6bf1feba6c78781bee5e0a8f15a9b47aa4cfd596cffb7d984b` |

Both leaf placements are four-byte aligned, have size 16, and use the common
unrelocated-text hash above. Both retain the same sole relocation to
`0x004CE3BC`.

The canonical Apple manifest records:

- `littlefs_file_rewind_private_source_replacement` at file offset 615,552,
  target `0x004CE460`, size 18, status
  `generated_source_entry_replacement`;
- `apollo_littlefs_file_rewind_private_source_leaf` at file offset 3,647,876,
  target `0x007B2964`, size 16, status `source_compiled`; and
- exact tiling of the 3,647,892-byte Apollo-main provider by 908 regions.

The effective Linux plan coarsens the appended overlay into the existing
`apollo_main_source_appended` region, while the overlay build report and
strict relocated-leaf record still authenticate the 16-byte Linux function at
offset 126,300 and runtime `0x007B3080`.

## Apple and Linux aggregate pins

| Artifact | Apple Clang 21.0.0 | Linux Clang 22.1.8 |
|---|---|---|
| overlay | 124,496 bytes / `9bda155bad5546bfd970b01cb565ba6dac18d4b624a9cd45bc3167cbf1793eca` | 126,316 bytes / `eea387bf745530cb810166a4779e5b32de9578cdeb41643440a096334113995e` |
| Apollo component | 3,647,892 bytes / `d9b009619108909ca326319f37be94a7b90c8a7523c4650f818f7d85ef1729b3` | 3,649,712 bytes / `535f1d7117d36073b8153fea3334cc53c692671da91baca443e3bd82db35851d` |
| assembled package | 4,426,346 bytes / `aadc9dc907c58708bca95ef91f6ff63e8bb9c6ff898da9a583add8b68fb9ce94` | 4,428,166 bytes / `6a08107f4bf3fbfcfa959056f121230488352ab5f1b89a3d2bfb07526c16776a` |
| `flash-plan.json` | 693,369 bytes / `0cf8c53e57627c4628399c21f65fbceeb75be033086e305b0fac58d442232c0b` | 583,448 bytes / `60bdc9a9bff4b70df9b88dcb3964ed13ccd0c77a91c48c9a6ad1c0077c8f46a9` |
| placed / unresolved / container-only regions | 964 / 2 / 5 | 817 / 2 / 5 |
| coarse source / generated / opaque bytes | 125,252 / 87,845 / 4,213,249 | 127,157 / 87,760 / 4,213,249 |

The Apple canonical ownership refinement is 125,267 source bytes, 87,982
generated bytes, and 4,213,097 opaque bytes. Relative to the immediately prior
production aggregate, this promotion adds 16 compiled-source bytes and 18
generated entry-replacement bytes while removing the same 18 stock bytes from
opaque ownership.

## Validation record

The following checks passed against the live repository inputs used for this
audit:

```text
python3 third_party/littlefs/verify_snapshot.py
  OK: v2.10.1 source-equivalent snapshot, BSD-3-Clause notice,
      bounded production allowlist, rewind provenance/hashes/ABI,
      no-format/no-erase policy, both official config spans,
      and Apollo rewind stock span/seam

python3 -m unittest tests.test_runtime_littlefs_file_rewind_private -v
  Ran 8 tests in 16.245s -- OK
```

The focused production suite covers exact source/header/upstream inputs;
1,010-case pristine differential behavior; compile-twice target-object,
section, symbol, and relocation closure; stock bytes, neighbors, wrapper,
caller, provider, and whole-image ingress; active Apple overlay generation and
patch bytes; canonical manifest tiling; stored Apple/Linux pins; active package
and flash-plan construction; and ownership accounting. A separate read-only
whole-image scan additionally confirmed the sole caller of the public wrapper.

## Safety exclusions and residual uncertainty

This promotion is intentionally narrow:

- The complete pristine `lfs.c`, `lfs_util.c`, and G2 block-device port are
  reference-only and are not registered wholesale in production.
- Private `lfs_file_seek_` remains an authenticated official provider at
  `0x004CE3BC`; the leaf's transitive behavior is not yet wholly source-owned.
- The selected v2.10.1 commit is a source-equivalent compatibility baseline,
  not proof of the vendor's exact historical Git checkout.
- The reviewed deterministic artifacts are limited to the pinned Apple Clang
  21.0.0 and Linux Clang 22.1.8 profiles. A different compiler/version must
  qualify new object, placement, relocation, aggregate, package, and plan pins.
- Whole-image ingress checking is bounded to decoded direct branch classes and
  stored pointer values; it is not a complete proof over arbitrary computed
  control flow.
- No image was signed or flashed, no hardware reset or boot was attempted, and
  no G2 filesystem was mounted or modified during this audit.

Do not call `lfs_format`, `lfs_migrate`, the recovered erase callback, or any
mutating littlefs API on G2 hardware until the project's separate read-only
golden-image, disposable-copy, power-loss, signing, and hardware-authorization
gates are satisfied.

## Final decision

**GO** for keeping `open_cfw_littlefs_file_rewind_private` as the production
source replacement for the exact Apollo-main stock span
`[0x004CE460,0x004CE472)`, using the pinned strict relocation to retained
`lfs_file_seek_` and the recorded Apple/Linux build profiles.

The GO is limited to source authentication, ABI/behavior equivalence, boundary
closure, deterministic overlay assembly, manifest/package integrity, and
offline build reproducibility. It makes no claim of on-device execution,
flashability under the vendor's signing policy, boot success, filesystem
safety on physical hardware, or complete removal of the remaining binary
provider.

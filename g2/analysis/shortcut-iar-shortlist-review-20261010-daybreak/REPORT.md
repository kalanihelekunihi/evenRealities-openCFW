# Bounded review of the ten saved IAR exact occurrences

**Implementation-review correction:** Original-instruction comparisons in `../iar-runtime-c-candidates-20261010-sol/REPORT.md` establish that `_UngetN` decrements consumed even for EOF. `__iar_zero_init3` writes a word before its unsigned continuation test; nonzero lengths 1–3 underflow, so the supported descriptor contract requires nonzero lengths at least four. The earlier arbitrary-length and EOF descriptions below are superseded by that verified contract.

Date: 2026-10-10  
Scope: private P2 evidence only  
Worker: Daybreak Blue Low, explicitly authorized after the requested Sol service failed

This review closes the concrete follow-up left by the fourth shortcut-theory
frontier: the ten exact IAR occurrences in
`../shortcut-cross-corpus-20261009-agent3/previously-unreviewed-shortlist.json`.
It does not change a canonical ledger, a review record, firmware source, an
authenticated input, or a workflow gate. `g2/workflow/state.json` remains
`P2_EXECUTING`; G2 through G6 remain unopened.

## Authentication and method

- The Apollo main oracle is the canonical fixed image
  `apollo_main-flash.bin`, 3,523,364 bytes, SHA-256
  `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`,
  loaded at `0x00438000`.
- Nine bodies were extracted from IAR 10.10.2
  `dl7Mx_tlns.a`, SHA-256
  `dc2e4966fda0c51fde5a9a30b5c9f6248033cde22336151c3f89cad1150db6f1`.
  `__iar_zero_init3` was extracted from `rt7Sx_tlg.a`, SHA-256
  `ef344d95207c8262b0a7f2b243f0f05941e995e841bda4d1ca017d50d7229150`.
- Native `arm-none-eabi-ar`, `readelf`, and `objdump` reproduced each symbol
  extent and showed byte-for-byte equality with its stock range. Direct Thumb
  `bl`/`b.w` references were counted across the whole authenticated image.
- To test whether an exact body identifies a unique DLIB configuration, the
  same symbol bytes were compared across every locally installed IAR 10.10.2
  `dl7*.a` or `rt7*.a` archive that contains the member. The equality sets are
  summarized below. This is stronger than treating the scanner's first
  deduplicated provider path as a unique producing archive.

## Results

| Stock range | Exact provider symbol | Direct refs | Bounded semantics | Same bytes in IAR 10.10.2 variants |
| --- | --- | ---: | --- | ---: |
| `0x595984..0x5959A2` | `isxdigit` | 2 | Returns true for ASCII `0-9`, `A-F`, or `a-f` | 17 |
| `0x567C80..0x567C9E` | `strcat` | 29 | Finds the destination NUL, copies source through its NUL, returns the original destination | 11 |
| `0x541B30..0x541B52` | `strcspn` | 5 | Counts the prefix containing no byte from the reject set | 17 |
| `0x567C64..0x567C80` | `__iar_Strrchr` | 2 | Tracks and returns the final occurrence of the requested unsigned byte, including NUL | 17 |
| `0x541B52..0x541B74` | `strspn` | 5 | Counts the prefix composed only of bytes from the accept set | 17 |
| `0x482684..0x4826B2` | `_PutcharsDefault` | 5 | Repeatedly calls a supplied output callback, updates the stream state/count, returns `-1` on callback failure | 17 |
| `0x4D15FA..0x4D161C` | `_GetN` | 10 | Advances scanner counters and calls the supplied get callback; returns `-1` when width is exhausted | 15 |
| `0x4D161C..0x4D1636` | `_UngetN` | 9 | Decrements consumed count and calls the supplied unget callback unless the character is EOF | 15 |
| `0x4D2112..0x4D2158` | `ranmatch` | 2 | Tests a byte against a scanf scanset, including three-byte `a-z` ranges | 17 |
| `0x5FA01E..0x5FA056` | `__iar_zero_init3` | 0 | Walks a zero-init descriptor stream, optionally rebases a flagged destination through `r9`, then clears words and a 0-3 byte tail | 6 |

The call topology adds useful context. `_GetN`, `_UngetN`, and `ranmatch` are
internal leaves of the adjacent IAR scanf cluster; `ranmatch` has exactly two
direct users inside the scanset path. `_PutcharsDefault` is an internal
formatted-output callback adapter. The five string/ctype leaves have ordinary
application/library callers distributed elsewhere in main. No direct branch
targets `__iar_zero_init3`, which is consistent with startup selecting it from
an initializer descriptor/table rather than with dead code; that observation
does not by itself recover the table contract.

## What this newly establishes

1. All ten historical catalogue extents have exact provider identities and
   straightforward bounded semantics. The shortlist contains no unknown
   application algorithm.
2. The three scanf helpers and the printf callback adapter bind the surrounding
   stock clusters more tightly to IAR DLIB's internal callback/state layout.
   In particular, `_GetN` uses state fields at offsets 12 and 16, `_UngetN`
   updates offset 12, and `_PutcharsDefault` updates stream fields at offsets 8
   and 44. These are ABI observations, not complete structure recovery.
3. `__iar_zero_init3` confirms the stock startup supports IAR's compact
   zero-initialization descriptor form. A set low bit in a destination word
   selects `r9 + value - 1`; unflagged values are used directly. The routine
   accepts arbitrary byte lengths and terminates on a zero length word.
4. The currently registered IAR 10.10.2 package is byte-compatible with these
   ten stock bodies. This is useful for reconstruction experiments after the
   implementation gates open.

## What the exact matches do not establish

The archive name recorded by the deduplicating scanner is not a producing
configuration fingerprint. The nine DLIB bodies repeat across 11-17 local
archives spanning `7M`, `7Mx`, `7Sx`, Normal/Full, and several suffix
variants. `__iar_zero_init3` repeats across six runtime archives:
`rt7MQx_tl.a`, `rt7M_tl.a`, `rt7M_tlg.a`, `rt7Mx_tl.a`, `rt7Sx_tl.a`, and
`rt7Sx_tlg.a`. Therefore these bodies do not select RWPI versus non-RWPI,
Normal versus Full DLIB, a unique architecture library, or a unique suffix.

They also do not prove that IAR 10.10.2 produced the July 2026 firmware. Shared
runtime leaves can remain unchanged across releases. The result supersedes the
narrow claim that no real EWARM archive was available for comparison, but it
does not supersede the consolidated conclusion that the exact producer release,
DLIB configuration, project options, ICF, link order, and initializer packing
remain unresolved.

The ten ranges still lack the independent canonical review and admission
required by the active campaign. Exact provider identity and this private
semantic review cannot be counted as accepted pseudocode coverage.

## Exhaustion boundary and next admissible inputs

This saved shortlist is now semantically reviewed as far as the present
third-party package can support. Repeating comparisons among the installed
10.10.2 archives will not distinguish the producing variant because the bytes
are demonstrably shared.

Further build-path discrimination needs at least one new authenticated input:

- the producing `.ewp`/`.eww`, ICF, linker map, or linker option receipt;
- an IAR release archive with a body that differs from 10.10.2 and also occurs
  in stock, allowing a release interval rather than a compatibility statement;
- the stock initializer descriptor/table boundaries and an independently
  reviewed startup call chain, to bind `__iar_zero_init3` to table layout and
  packing choices; or
- canonical P2 tasking and independent review for these exact extents.

No firmware implementation is justified by this report. The fourth frontier's
general third-party/dependency exhaustion claim remains valid, with the saved
ten-item review branch now closed.


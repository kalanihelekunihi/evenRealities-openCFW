# Apollo opacity wave 4: orientation/calibration numerical closure

Status: software-only, research admission; no hardware operation or production
routing.

## Reconciliation and graph closure

Wave 3 ended at 1,424 no-evidence rows / 185,480 official opaque bytes. The
wave-4 graph reaches eight rows that already contribute zero official opaque
bytes. One is the authenticated source-recreated IAR `memcpy` span at
`0x00439BE4`. Seven are interior callable boundaries nested inside the
oversized `[0x0043BA98,0x0043C08E)` envelope. Their bytes remain opaque but are
already counted once by that enclosing row; zero is not treated as proof of
independent source ownership.

Removing those eight duplicate/function-count rows leaves 1,416 actionable
rows / 185,480 bytes. Following every no-evidence call edge, including edges
through the zero-byte interior rows, closes after depth three:

| Depth | Positive-opaque functions | Bytes | Zero-opaque rows |
|---:|---:|---:|---:|
| 0 | 1 | 5,076 | 0 |
| 1 | 13 | 2,806 | 7 |
| 2 | 4 | 96 | 1 |
| 3 | 2 | 138 | 0 |
| **Total** | **20** | **8,116** | **8** |

The `0x0043C0E4` entry falls through to its separately emitted corpus
continuation at `0x0043C0EC`; the analyzer adds that authenticated provider
edge so the complete 102-byte IAR fill span is covered. The sole terminal
outside the closed tables is the already source-recreated IAR `sqrtf` at
`0x004397A8`. No actionable no-evidence call or provider-continuation target
remains.

Two decoded-body gaps are preserved honestly. The 5,076-byte root envelope
contains 4,952 decoded corpus bytes. `0x0043BA98` has a 1,526-byte envelope but
only a 276-byte decoded root body because the envelope contains the seven
separately callable zero-byte census interiors and alignment. All physical
envelopes are SHA-pinned.

## Positive and negative provider evidence

The corpus has exactly one caller of `0x0043A698`: `0x0055F848`. The
authenticated nPMX main-driver provider audit places `0x0055F848` inside an
eight-call Even first-party orientation/calibration seam. It explicitly
separates that seam from the admitted Nordic nPMX implementation. This is
positive context for the graph's role, not proof of the linked numerical
algorithm's historical source owner.

The liblc3 `0x43xxxx` census independently leaves the `0x43A698` float cluster
outside its attributed LTPF/bits set. The peripheral audit rejects the nearby
`0x0043A1B0` register-looking constants as a float/bitmask collision. There is
therefore no positive liblc3 or peripheral-provider basis for this closure.

Eighteen rows retain `typed-external-provider-unavailable`, with no source or
license claim. The `0x0043C0E4` entry and `0x0043C0EC` continuation are the
exceptions: existing provider maps and bounded audits identify their released
argument order and complete `memset`-family IAR DLIB span. Both are recorded as
`typed-external-iar-dlib-source-unavailable` with proprietary/unavailable
license status, not reimplemented or relicensed.

## Accounting

| State | Functions | Bytes |
|---|---:|---:|
| Wave-3 residual | 1,424 | 185,480 |
| Reconciled zero-opaque graph rows | 8 | 0 |
| Before wave 4 | 1,416 | 185,480 |
| Newly typed | 20 | 8,116 |
| After wave 4 | 1,396 | 177,364 |

The next largest envelope is 5,056 bytes at `0x00519290`. Production admission
remains prohibited without exact provider/source/license evidence and an
honest code-generation, relocation, ABI, and placement recipe. The analyzer
performs no signing, flashing, probing, or other hardware access.

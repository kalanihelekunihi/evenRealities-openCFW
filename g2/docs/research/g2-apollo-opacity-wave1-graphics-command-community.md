# Apollo opacity wave 1: graphics-command community

Status: software-only, research admission; no hardware operation or production
routing.

## Selection

The current unanchored census contains 1,873 no-evidence functions / 290,704
official opaque bytes. Reconciliation against the checked-in dedicated family
waves removes boundaries already classified after that parent census:

| Boundary wave | Parent no-evidence rows | Bytes | Current disposition |
|---|---:|---:|---|
| Cordio/`0x5Dxxxx` sea | 300 | 52,866 | 102 source-attributed plus 198 source-admitted |
| FreeType base community | 81 | 6,928 | authenticated FreeType 2.9.1 source admission |
| liblc3 encoder community | 31 | 14,434 | source-attributed family boundary |
| Apollo510 MSPI triplet | 3 | 6,250 | authenticated BSD source candidate |
| **Current residual before wave 1** | **1,458** | **210,226** | unclassified |

Existing per-module function maps were already consumed by the parent census's
`closed-module-manifest` tier and are not subtracted again. The four SHA-pinned
non-census boundaries adjacent to the closed `0x5Dxxxx` census are reported by
the reconciliation but likewise are not part of the parent no-evidence total.

After those exclusions, `0x005202EC` is the largest trustworthy remaining
function envelope: 8,374 official bytes. Its complete authenticated corpus body
directly calls nine local state/command-building leaves at `0x0052262E`,
`0x0052264E`, `0x005226B2`, `0x005226E8`, `0x005228B0`, `0x00522920`,
`0x0052294C`, `0x00522956`, and `0x00522A16`. The bounded batch therefore
covers ten functions / 9,002 bytes within the non-contiguous community range
`[0x005202EC,0x00522A20)`.

## Disposition

The community constructs float-heavy command/state records and bitfields, but
positive evidence does not identify a redistributable source body:

- the peripheral census classifies the root's `0x4xxxxxxx` hint as a constant
  collision, not a validated peripheral address;
- callers cross LVGL, first-party, and unresolved boundaries;
- the root calls a rejected oversized envelope and multiple unresolved `0x51`
  helpers;
- neither the authenticated LVGL nor AmbiqSuite source snapshot contains an
  exact source definition for this body; and
- G2's Ghidra envelope is 8,374 bytes while its decoded instruction body is
  8,300 bytes, so the 74-byte tail is retained as authenticated envelope data,
  not silently declared executable source.

All ten rows are consequently `typed-external-provider-unavailable`. This is a
non-opaque, SHA-pinned boundary with a precise reason, not an implementation or
a speculative Nema/LVGL attribution. It may be replaced only after provider,
ABI, configuration, and complete call/data closure are authenticated.

## Accounting

Wave 1 moves ten functions / 9,002 bytes from unclassified to typed external:

| State | Functions | Bytes |
|---|---:|---:|
| Before | 1,458 | 210,226 |
| Newly typed | 10 | 9,002 |
| After | 1,448 | 201,224 |

The analyzer authenticates the official image, parent and family manifests,
source-admission reports, exact body hashes, corpus markers, direct-call counts,
and the static typed-boundary table. It performs no signing, flashing, probing,
or hardware access.

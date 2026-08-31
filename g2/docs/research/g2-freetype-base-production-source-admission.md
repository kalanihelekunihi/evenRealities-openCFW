# G2 FreeType 2.9.1 base production-source admission

Date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Mode: software-only; no signing, flashing, erase, or hardware operation

## Result and selection

After the existing TrueType and CFF admissions, the base cluster is the
largest exact function-level FreeType mapping not already represented by a
maintained component. The inherited base census authenticates 83 functions and
7,874 stock bytes. Seven Mac/resource-fork fallback bodies are separately
authenticated to upstream `ftobjs.c`; they add 1,862 physical bytes outside
the 83-function census. The reconciled admission is therefore 90 functions and
9,736 bytes, without subtracting or counting the fallback bodies twice.

The selected FreeType 2.9.1 base implementation consists of `ftbase.c`, its 18
amalgamated `.c` inputs, `ftinit.c`, and `ftbitmap.c`: 21 hash- and Git-blob-
authenticated files totaling 429,079 bytes. This is implementation inventory,
not a claim that every emitted function is one of the 90 mapped stock bodies.

## Maintained boundary

`components/shared/freetype_base` provides caller-owned allocator ports and
the recovered initialization order:

```text
allocate FT_MemoryRec -> install callbacks -> FT_New_Library
                      -> FT_Add_Default_Modules -> verify ten modules
```

It preserves upstream face autodetection and exposes optional TrueType-only or
CFF-only selection through the public `FT_OPEN_DRIVER` interface. Face
reference, release, glyph load, and render operations remain behind public
FreeType APIs.

The maintained lifecycle deliberately uses `FT_Done_Library` before releasing
the separate memory record. The stock audit found no safely assignable
`FT_Done_FreeType` entry, so this teardown is reviewed source policy rather than
a claimed stock callsite identity.

## Mapping blockers beyond base

The official module table authenticates the following additional classes but
the reviewed engine census and four sealed opacity source-boundary inputs have
zero exact function-level mappings for them:

| Module class | Class address | Reviewed function mappings |
|---|---:|---:|
| autofitter | `0x00752520` | 0 |
| psaux | `0x00758A18` | 0 |
| psnames | `0x00758A60` | 0 |
| pshinter | `0x00758A3C` | 0 |
| sfnt | `0x0075A3F8` | 0 |
| smooth | `0x00718D9C` | 0 |
| smooth-lcd | `0x00718DD8` | 0 |
| smooth-lcdv | `0x00718E14` | 0 |

Class presence and source availability do not establish function ownership.
These modules remain blocked on exact stock mapping; this tranche does not
infer ownership from address order, string proximity, or upstream similarity.

## Deterministic qualification

The admission analyzer reruns the existing 83-function base-cluster analyzer,
authenticates the official stock image and ten-module record, verifies all 21
source identities against the pinned FreeType provenance, checks the maintained
API and component admission, and fails if the component appears in the Apollo
overlay or builder. The checked manifest carries every source and mapping
record plus the eight explicit next-module blockers.

The focused runtime gate builds the maintained adapter with the actual selected
FreeType 2.9.1 module set. It tests the exact ten modules, exhaustive injected
initialization-allocation failure cleanup, upstream and strict face policies,
and real glyph rendering. It also compiles both adapter units and all three
selected base translation units for Cortex-M55 Thumb hard-float with
`-Wall -Wextra -Werror`.

Reproduce with:

```sh
cd g2
python3 tools/analyze_g2_freetype_base_source_admission.py --check-manifest
python3 -m unittest -v \
  tests.test_runtime_freetype_base_admission \
  tests.test_freetype_snapshot
```

## Evidence bounds

No authenticated target placement or production overlay route exists. Source
admission does not establish IAR compiler-byte identity. External G2 font
payload identities, runtime face-path arrays, final section budget, stack/WCET,
and scheduler interaction remain unresolved.

Hardware validation is blocked because this software-only tranche had neither
authorized physical G2 hardware nor an authenticated external font payload.
No live rendering behavior is claimed.

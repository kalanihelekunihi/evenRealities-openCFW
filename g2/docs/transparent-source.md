# The transparent-source pipeline

This document describes how the G2 Ghidra analysis data becomes a compilable C
codebase, and how that codebase becomes an Apollo main image with no opaque
spans in it. It also states, as plainly as possible, what that image is not.

The measured result of the current run is in
[`transparent-source-ledger.md`](transparent-source-ledger.md), which is
regenerated from the build and never edited by hand.

## The problem this solves

The existing `source` profile reproduces the official Apollo payload by taking
the vendor image as a base and replacing regions with compiled source, one
reviewed closure at a time. That model is correct and byte-exact, and after a
long run of closures it owns roughly 143 KB of a 3.5 MB image. Everything else
is carried forward as **opaque base bytes**: spans that are present in the
output because they were present in the input, with no source behind them.

The transparent profile inverts the default. Instead of asking *what have we
replaced so far*, it asks *what does every byte in this image consist of* —
and refuses to emit any byte that no source unit produced.

## The four stages

```
analyzed Ghidra project
        |
        |  harvest_ghidra_decomp.py            (make transparent-harvest)
        v
research/corpus/apollo-main/ghidra/decomp/     7,449 functions, decompiled
        |
        |  build_transparent_function_db.py    (make transparent-db)
        v
build/transparent/function-db.json             every function, every tier
build/transparent/region-map.json              gapless cover of the image
        |
        |  generate_transparent_source.py      (make transparent-source)
        v
build/transparent/source/                      one C unit per function,
                                               plus declared data arrays
        |
        |  build_transparent_image.py          (make transparent-image)
        v
build/transparent/image/                       an image with no opaque spans
```

### 1. Harvest

`harvest_ghidra_decomp.py` runs headless Ghidra against an already-analyzed
project, sharded across worker copies so the evidence it reads is never
mutated. For each function it exports the decompiled C, the recovered
prototype, the calling convention, the callee set, the exact address ranges of
the body, and the SHA-256 of the stock bytes those ranges cover.

The harvest refuses to run against the wrong program: `--expect-executable-sha256`
pins the analyzed payload to the authenticated Apollo blob.

Function bodies are address *sets*, not intervals. 107 Apollo functions are
split across several ranges, and treating them as `min..max` would silently
swallow whatever sits in the holes — so the real ranges are carried through
the whole pipeline.

### 2. Reconcile

Four independent sources describe these functions, and each knows something
the others do not:

| Source | Contributes |
| --- | --- |
| the harvest | bounds, bodies, prototypes, callees |
| `g2-apollo-unanchored-census-functions.tsv` | provider family, evidence, confidence |
| 205 `*-function-map.tsv` manifests | real names, behavior notes, upstream routes |
| `core_overlay/overlay.json` | which functions already have reviewed source |

`build_transparent_function_db.py` merges them into one address-keyed database
and assigns each function the strongest tier any input can justify:

    unrecovered < decompiled < identified < attributed < candidate < source

It then walks the image once and emits a **gapless cover**: every byte lands in
exactly one region, either a function body range or a classified gap between
them. Gaps are classified — vector table, pointer table, string pool, zero
fill, data — so that later work can attack them by kind. The build fails if
the cover does not total the image exactly.

### 3. Generate

`generate_transparent_source.py` writes one translation unit per function.

Raw decompiler output is not C: it names types the decompiler invented, calls
helpers that do not exist, and disagrees with itself between units.
`tools/transparent/openg2_decompiled_runtime.h` supplies the missing
vocabulary, and each unit gets declarations derived **from its own body**:

* A data symbol is named after the address it lives at, so it resolves to that
  address directly — `DAT_004452c8` becomes `(*(undefined4 *)0x004452C8u)`.
  Nothing is left as an undefined extern, and the declaration form follows how
  the unit actually uses the symbol: called, called through, indexed, or read
  flat.
* A callee keeps its recovered return type but loses its parameter list.
  Ghidra analyzes each call site independently of the callee, so the same
  function is routinely called with three different arities in three different
  units. An unprototyped declaration accepts all of them.
* A function whose recovered control flow jumps to a label it never defines is
  not repaired. It gets a trap, and its decompilation is preserved beside it
  under `#if 0` for review.

Compiling each function as its own unit is what makes this work: a type
disagreement between two functions cannot cascade, because they never share a
declaration.

Non-code regions are emitted as declared byte arrays, each stating its address,
its classification, and the hash it must reproduce.

### 4. Place

`build_transparent_image.py` compiles every unit and lays the results into the
image at their **stock addresses**.

Address preservation is not a nicety here. Recovered code is saturated with
absolute references — `DAT_004452c8` *is* 0x004452C8 — so relocating a function
would quietly invalidate every one of them. Keeping the stock map means the
recovered references stay meaningful and only calls need relocating.

A function is placed if its compiled form fits its stock envelope. Because the
stock image was built by IAR at high size optimization, recompiled decompiler
output is frequently a few bytes larger, so a unit that does not fit is rebuilt
under a series of alternative optimization settings and the first result that
fits wins. The variant that produced each placed function is recorded.

What does not fit gets a `BKPT #0` trap. So does a unit that did not compile,
and so does the tail of a split-range function. The builder then verifies that
every byte of the image was written by exactly one region, and generates the
32-byte staging header from the assembled result.

#### Why the remaining functions do not fit

Most functions that compile also place. The ones that do not are limited by a
structural difference rather than by optimizer tuning. Consider a six-byte
stock function whose whole body is one store:

```c
void FUN_0043d0c8(undefined1 param_1)
{
  *DAT_0043d13c = param_1;
  return;
}
```

IAR compiled that to six bytes because the address `0x0043D13C` was not in the
instruction stream at all: it sat in a literal pool shared by neighbouring
functions, reached by a two-byte PC-relative load. Those pools are exactly the
inter-function gaps this pipeline classifies as data and emits verbatim.

The generated unit resolves `DAT_0043d13c` to its address directly, which is
what makes the unit self-contained and free of undefined externs — but it costs
a `movw`/`movt` pair, eight bytes, inside the function. The function is now
fourteen bytes and cannot fit where six bytes used to be, while the literal
pool it no longer uses still occupies its own bytes elsewhere in the image.

This is not expressible away in C: a translation unit cannot be told to reach
into a specific shared literal pool at a fixed address. Retrying under
alternative optimization settings recovers a few dozen functions at the margin
and nothing more. The overflow histogram in the ledger shows the shape of what
is left — the bulk of it sits within eight bytes of fitting, which is one
`movw`/`movt` pair minus the two-byte pool load it replaced.

The other trap classes are smaller and different in kind. A few hundred
functions reference symbols that do not exist anywhere in the image: Ghidra
models some Cortex-M instructions as calls to invented helpers
(`isCurrentModePrivileged`, `VectorSignedToFloat`), and stack artifacts like
`stack0xfffffff8` are recovery failures rather than real storage. Those cannot
be resolved by declaring them harder, and they trap.

The way out for the overflow class is to stop constraining recovered code to
stock envelopes — lay the compiled functions out in a fresh text region and
rewrite the references to them. That is tractable because the pipeline already
knows every function's address and every pointer table in the image, but it is
a different design from the address-preserving build described here, and it
would have to rewrite the vector table and every recovered pointer table to
match. It has not been done.

## What the result is

An Apollo main image, the correct size, at the correct addresses, in which
**every byte has a source unit behind it**: recovered code compiled from C,
declared data arrays, or an explicit trap. The `opaque_bytes` count is zero,
and that is a checked property of the build, not a claim.

It is worth being precise about which of those three dominates. 7,217 of 7,449
functions compile and 5,125 of them place, so about half the image's code bytes
are compiled from recovered C; the rest of the image is declared data, which is
the larger share by byte count, and traps. The ledger gives the exact split.

The codebase remains more complete than the image built from it: every function
that compiles is readable, addressable C in the tree whether or not it fits its
stock envelope.

## What the result is not

**It is not known to run.** This is the important sentence in this document.
Ghidra decompilation is recovered *structure*, not reviewed *behavior*. A unit
that compiles has been made syntactically well-formed; nothing in this pipeline
establishes that it computes what the stock code computed. Several deliberate
choices trade fidelity for compilability — widening void returns to machine
words, dropping parameter lists, treating indirect call results as values —
and each one is a place where recovered code can diverge from stock behavior.
Nothing here should be flashed to a device with any expectation of working.

**Declared data is not reconstructed data.** Fonts, bitmaps, tables and string
pools cannot be recovered by a decompiler. Emitting them as C arrays makes them
visible, addressable, and editable, and records where each one belongs and what
it hashes to. It does not explain them, and it does not make them any less
vendor-derived. The ledger counts them separately for exactly this reason.

**Traps are failures, stated as failures.** Where the corpus establishes
nothing, the image halts rather than running plausible invented behavior. That
is the same commitment the rest of openCFW makes at its provider boundaries.

## Relationship to the `source` profile

The two profiles answer different questions and neither replaces the other.

| | `source` | `transparent` |
| --- | --- | --- |
| Base | official payload | nothing |
| Unexplained bytes | ~3.4 MB, counted | none, by construction |
| Behavior | stock, except where reviewed source replaced it | unverified wherever recovered code was placed |
| Byte-exact against stock | yes | no |
| Answers | what have we replaced so far | what is every byte made of |

The transparent build makes the remaining work legible and mechanically
trackable: every trap is a named function at a known address with its
decompilation, its provider family, and its confidence already attached. As
reviewed source lands for a function, its tier rises to `source` and it stops
being recovered output — the same promotion path the `source` profile has
always used, but with the whole image enumerated rather than only the part
already closed.

## Reproducing

```sh
make transparent
```

That runs the database, generation, placement, and ledger stages against the
checked-in harvest. Re-harvesting needs Ghidra, a JDK, and an analyzed project:

```sh
OPENCFW_APOLLO_GHIDRA_PROJECT=/path/to/project make transparent-harvest
```

The pipeline's own tests do not need Ghidra:

```sh
make transparent-test
```

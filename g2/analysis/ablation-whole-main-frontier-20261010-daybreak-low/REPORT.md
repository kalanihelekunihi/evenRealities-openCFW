# Ablation whole-main callable frontier — 2026-10-10

Status: bounded tool-specific frontier exhausted. This pass adds a reproducible
rule for using Ablation on the authenticated Apollo main image. It does not add
accepted pseudocode, identify a new provider, reconstruct firmware, or advance a
gate. `g2/workflow/state.json` remains `P2_EXECUTING`.

## Authenticated inputs and scope

The analyzed stock OTA SHA-256 is
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
The existing full-payload analysis ELF SHA-256 is
`36c9b79de3b961d36ad343a1402a112298603111cbe1d5875e1b471694159d1a`.
Its bytes are the authenticated payload in an authored ELF envelope; its ELF
metadata is an analysis aid, not producer evidence or a replacement image.

The comparison uses all 8,853 retained historical function records, reduced to
8,853 unique entries, from `functions-000.jsonl`. Their body ranges bound the
native oracle. Ablation is pinned at
`97e051b44d1ac8129b35556fe533e6e8b5338db2`; GNU objdump reports
`GNU objdump (GNU Binutils) 2.47.20260726`.

## Tool behavior established

Unadapted `BinaryContext.build` finds one authored static ELF symbol, no Thumb
functions, no call edges, 30,789 printable byte runs, and no string xrefs. It
does not discover the stock function corpus or useful referenced strings from
this view. The printable runs cannot be promoted as data or strings.

The bounded adapter supplies the already reviewed function starts and Thumb
state in memory, then asks Ablation to rebuild its call graph. Ablation reports
74,816 direct-call edges. GNU force-Thumb decoding finds 71,344 `BL`/immediate
`BLX` calls inside retained body ranges. Of those, Ablation contains 70,146.

Every one of the 1,198 missing body calls belongs to one of 23 functions whose
next-start span exceeds Ablation's hard 4,096-byte per-Thumb-function scan cap.
There are zero missing body calls among uncapped functions. This is a useful
and independently checked positive boundary: with reviewed starts/state and a
span no larger than 4 KiB, Ablation is a complete direct-immediate-call
inventory shortcut for this corpus.

The whole-image graph is not directly admissible. It includes 4,670 calls not
in retained body ranges. GNU independently decodes 4,661 of them between
retained ranges, meaning Ablation assigned gap/data code to the prior function.
Nine more are not present in the GNU body-or-gap call multiset and are consistent
with the implementation's initial aligned ARM-word scan and the terminal mapped
data span. Ablation stores only `(owner,target,label)` for graph edges, so a
downstream reviewer cannot recover the site and filter these results back to the
authenticated body ranges.

Indirect register calls are outside this inventory. The tool scans only direct
`BL` and immediate `BLX`; no claim is made about callback tables, virtual calls,
or register-indirect dispatch.

## Reconstruction facts and admissibility rule

The result corroborates 70,146 existing direct callable relationships against
two decoders. It does not create 70,146 new semantic identities: the historical
range inventory and authenticated bytes supplied the boundaries.

Use Ablation direct-call output only when all of the following are retained:

1. authenticated original bytes and load address;
2. independently reviewed Thumb state;
3. an exact body range no larger than 4,096 bytes;
4. call-site-bearing profile output, checked against native decoding.

Do not use whole-image `BinaryContext.call_edges` as canonical coverage. Split
larger bodies into reviewed ranges and retain call sites. Do not treat raw
printable runs as strings without a proved literal/data reference. Enumerate
indirect calls separately from original instructions and relocation/data
metadata.

This exhausts the current pin's additional whole-main shortcut value: expanding
the scan cannot solve the hard cap, missing static Thumb discovery, loss of call
sites, gap ownership, indirect calls, or string-reference absence. Those require
reviewed metadata or a different oracle, not another unbounded Ablation replay.

## Reproduction

From the repository root:

```sh
PYTHONPATH="$PWD/third-party/tools/ablation" \
  /Users/kalani/Repos/ablation/.venv/bin/python \
  g2/analysis/ablation-whole-main-frontier-20261010-daybreak-low/analyze.py

/Users/kalani/Repos/ablation/.venv/bin/python \
  g2/analysis/ablation-whole-main-frontier-20261010-daybreak-low/verify.py
```

`evidence.json` retains hashes, exact counts, representative discrepancies,
tool identities, and the comparison method. `objdump.stderr.txt` is retained to
show the native decoder completed without diagnostics. `preservation.json`
records the unchanged workflow, gitmodule, tool pin, and gate state.

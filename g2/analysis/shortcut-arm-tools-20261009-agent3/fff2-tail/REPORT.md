# Stock 0xFFF2 tail: initialization proved, persistent ownership qualified

The locked image independently supplies both zero tail bytes during ordinary scatter initialization. Executing its real zero initializer, then `HciVscUpdateNvdsParam`, yields `FF 7C 01 0F B8 19 00 00`; the newer Ambiq reference is not needed to derive those bytes. The command routine itself writes only six bytes and does not reinitialize its tail on subsequent calls. A persistent lifetime invariant still requires exclusion of indirect/calculated writers and unknown executable regions.

## Authentication and command semantics

Full main payload SHA is `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`. Original body `[0x004B4C8A,0x004B4CB2)` matches historical independently bounded SHA `db6ec37887401e6aa5d37c1308fccca367048a6306546127f427a3cf75898ec8`. Literal `0x004B4DC0` contains `0x20074150`. GNU force-Thumb disassembly shows six byte stores at PCs `0x004B4C90`, `94`, `98`, `9C`, `A0`, `A4` to offsets 0–5, and call arguments `(opcode=0xFFF2,length=8,source=0x20074150)`.

`HciVendorSpecificCmd` at `[0x0052B84C,0x0052B87A)` preserves source r2 in r5, allocates a command with the byte-length argument, and on successful allocation calls original copy helper `0x00439BE4` with `(destination=command+3,source=buffer,length=8)`, then sends the command. It passes a copied payload, not the source pointer, to the send routine. GNU listing is retained. Allocation/send behavior is outside this fixture.

## Actual initializer and direct writers

Scatter record at `0x0075D3C8` selects Thumb handler `0x005FA01F`; its arguments start at `0x0075D3CC`. The real handler `0x005FA01E` clears `[0x20004558,0x20075048)`, including `[0x20074150,0x20074158)`. This independently reproduces the existing initializer observation in `g2/analysis/audio-logger-provider-composition-2026-10-09/`, with full payload authentication first. Its earlier raw SHA `19044a72…` refers to headerless `raw[32:]`, not a different image.

The private fixture prefilled the complete 461,552-byte span with A5 and executed original instructions until just before the next scatter record. It verified every byte zero. For this buffer the observed zero stores are 32-bit writes at `0x20074150` and `0x20074154`, both from PC `0x005FA034`; the latter initializes bytes 6–7. It then executed the original command prefix and confirmed all three call arguments and the eight-byte payload. No startup success, scheduling or physical execution is claimed.

Known direct writes to the exact buffer are therefore:

| Writer | Extent | Evidence |
| --- | --- | --- |
| Scatter zero handler | offsets 0–7, two word stores | Original-byte execution and GNU listing |
| HciVscUpdateNvdsParam | offsets 0–5, six byte stores | Original-byte execution and GNU listing |

No additional direct tail write surfaced in the current static-reference scan. The fixture sets tail=A5 5A and invokes the original command again: output becomes `FF 7C 01 0F B8 19 A5 5A`, proving this routine inherits preexisting tail state. Original authenticated copy helper was separately executed at command-style unaligned destination `+3`: both the zero-tail and A5-5A payloads were copied exactly, with source unchanged and surrounding destination sentinel bytes intact. Historical copy SHA `8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd` hashes the complete bounding extent `[0x00439BE4,0x00439C8A)`, including its gap; concatenating the recorded discontiguous body ranges instead hashes to `f9131d437adf46e50c1705f7b28e33d7671cde732e46d799106da7d6f9438d79`. The initial fixture correctly rejected their apparent equality; it now authenticates the historical hash under its actual bounding-extent convention. No allocator mock was used.

## Static references and neighboring ownership

`probe.py` scans two-byte-aligned original payload words for pointers within ±64 bytes of the buffer, and Capstone-decodes each recorded historical Thumb body to collect PC-relative literal references. `results.json` preserves all nearby literals and all observed references, function names/sites, corpus ledger hash and counts. The sole exact pointer literal is `0x004B4DC0`; its sole decoded PC-relative reference is the command's `ldr r2` at `0x004B4C8C`. No literal points directly into offsets 1–7, and the scanned corpus has no candidate `movw #0x4150`/`movt #0x2007` sequence. This scans known functions, not the still-open whole-image denominator.

The closest competing owners were checked rather than assuming adjacency proves isolation:

- Base `0x20074148` belongs to the six-byte BD-address path. HciDrvRadioBoot copies four bytes then writes offsets4/5; HciVscSetCustom_BDAddr copies exactly six bytes; HciVscUpdateBDAddress reads it. Those discovered writes end at `0x2007414E`, before this buffer.
- Base `0x20074158` is FreeRTOS free-list sentinel storage. `prvHeapInit` writes offsets0 and4, starting immediately after this buffer. Its normal forward stores do not overlap the tail.
- Base `0x20074140` is an indexed pointer array: `FUN_00597C6C` writes at `base+index*4`, so an unconstrained index4/5 could overlap this buffer. Its sole discovered direct caller `FUN_00597CAE` writes count=2 immediately before invoking it; GNU confirms the callee loop tests unsigned index<count before its indexed store. On this observed call chain, indices0/1 touch only `[0x20074140,0x20074148)`. The lookup `FUN_00597D10` only reads the indexed array. This is conditional on the discovered direct caller set and normal sequential execution; no unknown indirect invocation/count corruption is excluded.

Other nearby reference sites are retained for independent review rather than labelled direct tail writers without address/extent evidence. Generic memcpy/memset, indirect pointers, arithmetic using remote bases, interrupts, DMA, external ROM and uncovered code are not exhaustively bounded by this scan. Broader pointer-to-target exclusion would require whole-corpus P2 ownership and alias analysis, not a stronger wording of this result.

## Defensible conclusion and finite boundary

Confirmed: stock initializer zeros bytes6–7, the original command preserves them, and the original copy includes them. Strong bounded evidence: the eight-byte initialized payload equals the official Ambiq mask and the observed direct/static neighbors preserve its tail on their reviewed paths. Qualified: claiming every live/reset command always has zero tail requires complete exclusion of other writers and proof of reset/startup ordering across all relevant entries.

This closes the finite initialization question and leaves a precisely scoped persistent-ownership obligation. No new source download, canonical project/ledger edit, source implementation or gate change occurred. No classifier denial or model switch occurred. All execution and scan outputs live in this private directory.

Replay: `/Users/kalani/Repos/ablation/.venv/bin/python g2/analysis/shortcut-arm-tools-20261009-agent3/fff2-tail/probe.py` (existing Unicorn dependency at `/tmp/mspi-enable-python-deps`).

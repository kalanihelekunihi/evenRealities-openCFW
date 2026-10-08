# PCM2.2 selector 3 add-on proof

Selector 3 is the stock routine at `0x4283e2..0x428506` (292 bytes), SHA-256
`f87a46ff367ce309a8fbd0ce1c0ae0097f00de2b4c898858d966df1da688f7c7`. The
authenticated scatter table maps slot 3 to `0x4283e3`. The isolated source
implementation is `handler3.c`; it reuses the frozen base ELF's native TON
adjustment, timer service, and delay functions. It does not include or copy the
upstream SDK file. Upstream Ambiq PCM2.2 `transition_sequence_3` is corroborating
evidence; the implementation retains the upstream BSD-3-Clause attribution.

`make verify` passes seven direct stock/source fixtures and one naturally
reached callback comparison. The direct fixtures cover nonuniform rank/profile
inputs, state pairs, and a timer-ready state 26 path. The stock routine's
instructions were visited at 268 of 292 bytes across those fixtures; the
remaining bytes are conditional paths not exercised by these inputs. The
natural fixture starts both sides at the actual event-A callback (`0x42a878`
stock, its source counterpart), with the real stock decoder or compiled source
installer populating the callback table. Selector 3 is reached from stock
caller `0x42a542` with arguments `[19, 7, 6, 6]`. Stock and source both complete
with status 0 and major state 19; the final tracked state, four MMIO writes,
argument memory, and ROM wait argument match.

For the natural callback comparison, the test validates the source-installed
table and then replaces only slot 3 in emulator RAM with the add-on entry. No
shared source table or frozen ELF is changed. The ROM wait entry at `0x40` is a
synthetic immediate return that preserves R0 and records its argument; the
natural fixture has the timer disabled. The direct timer-ready fixture runs the
actual linked timer-service implementation. Profile core/tempco/VDDCLV fields
and peripheral register values are deterministic synthetic inputs; rank words
come from the decoded initializer. These offline checks do not establish
physical-device behavior or byte identity with the locked routine.

Receipts: `comparison.json` (direct fixtures) and `comparison-natural.json`
(natural initialized-data callback). Re-run with `make verify`; the base ELF
path and its expected digest are pinned in `verify.py`.

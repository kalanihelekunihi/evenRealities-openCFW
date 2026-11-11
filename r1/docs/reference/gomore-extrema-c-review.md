# R1 moving-average extrema extraction in C

`native_gomore_extrema.c` supplies the eight-word stock ABI at `0x647c4`.
The [receipt](gomore-extrema-c-review.json) binds production source/object, REA,
direct/caller replay, defect controls and qualification. No assembly or persistent
RAM is added. The guarded generic utility retains its separate capacity/size_t
and delayed-publication behavior under the `_checked` name.

The C helper retains signed count/offset tests with wrapped word arithmetic,
unsigned window-to-float conversion, left replication and right clamping, ordered
sliding subtraction/addition and signaling FP comparisons. It publishes peak
indices immediately as bytes and reloads the current sample after publication.
Counts have the stock initial, successful and overflow store orders; each list
has capacity twenty, and overflow resets count bytes while retaining earlier
array writes. There is no final pending-extremum flush. Four volatile stack
parameters preserve the native live pointer loads, including pointers that mutate
the incoming argument words.

The production object passes **2,881 native/C pairs**, including **35 faults**
and **192 capacity overflows**. Checks include exact byte writes, surrounding
memory, argument-word aliases, partial failures, invalid access address/width,
raw return, FPSCR, restored SP and preserved integer/FP registers. Inputs cover
zero/negative counts, zero windows, the wrapped maximum window, raw FP specials,
several rounding modes, buffers overlapping samples and indices beyond 255.
Independent sequence checks cover equal-window no-output behavior, the twenty-entry
limit, wrapped peak/minimum indices with right-edge transitions, and publication
before reloading an aliased current sample. Eight compiled defects are rejected,
including cached stack arguments and reordered sample publication.

The actual native optical estimator passes **112 heavy-path caller pairs**, with
**136 C extrema calls**. C append and compaction are also substituted. The native
filter, candidate matchers, interval merger, mode selection and fallback code
execute from stock. Context/output bytes, external write order, raw root return,
FPSCR and all eight extrema arguments agree. Other linked C math/configuration
objects are not claimed exercised by these heavy cases. The optical root and
remaining selectors are still unfinished C dependencies.

The native extrema frame is sixty bytes; the C profile owns seventy-two. Private
frame bytes are excluded. Extremely large windows that would require billions of
iterations and physical FP alignment behavior remain outside replay coverage.
No physical-device validation or full source-only final link is claimed.

The normal build compiles **696 units**, without failures or duplicate strong
symbols, with unchanged **179 application / 34 bootloader imports**. All **694 prior
units** outside the renamed generic owner retain source/object hashes. Scoped
qualification selects no executable replacement. The canonical plan stays unchanged,
and hybrid equality still passes with **4,381 source-built executable bytes**,
**641,779 stock executable bytes** and **248 resource bytes**. These results do not
establish complete C reconstruction or executable byte identity for this helper.

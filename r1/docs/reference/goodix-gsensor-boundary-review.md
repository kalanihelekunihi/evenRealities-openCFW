# Goodix accelerometer callback boundaries

REA analysis of the locked R1 application locates the sample handoff at
`0x6f920` and cache-start operation at `0x6f964`. These remain unimplemented
source routes. This review records prerequisites for replacing the unresolved
SDK `gh3026_gsensor_data_get` seam rather than assuming that a similarly named
board function has the same contract.

The sample routine loads the optional board callback from `0x2002fd30` and
explicitly prepares only R0 with the sample-buffer address before BLX. R1 still
contains the incoming count pointer in the observed native instruction path;
absence of an explicit second-argument move does not prove that the callback
has a one-argument signature. Its producer and concrete target must establish
that signature. The earlier shorthand description of this as a one-argument
hook is therefore insufficient for ABI selection.

After the optional board call, stock reloads the unsigned 16-bit count on each
iteration. It loads each six-byte sample's signed axes in Z/Y/X memory order,
then calls `0x2adfc` with timestamp zero and X/Y/Z sign-extended argument words.
It reloads count again after the last sink call. Only after processing samples
does count greater than 100 enter the self-loop. Moving that guard before the
loop, snapshotting count, or changing axis load order would alter this boundary.
The stock inventory identifies `0x2adfc` as a two-byte sample-sink no-op; any
source replacement must verify those bytes rather than import SDK algorithm
behavior under that name.

Twelve controlled stock executions confirm zero/one/100/101 counts, optional
board callback, hook-produced count changes, sink-induced growth/shrinkage,
signed axis arguments, Z/Y/X halfword reads and the post-loop nonreturn guard.
The probe observes the live second argument register as the count pointer.
It models callback effects and does not establish full source equivalence.

The cache-start routine captures the formatter pointer at `0x20007b04`, reserves
184 scratch bytes, clears 180 bytes via `0x277aa`, then calls the captured pointer
with scratch/180/message. It next reloads the optional plain logger at
`0x20007b00`, calls `0x2adfa`, and finally reloads the optional cache callback
at `0x2002fd28`, restoring its frame before tail dispatch. These are additional
state ownership and frame obligations; the simpler SDK cache-start body alone
does not represent them.

Next implementation work must establish the callback-table producer and shared
storage ownership, verify both two-byte sink/hook bodies, and preserve live
count/axis access behavior. Cache-start also needs scratch/frame and logger
ownership evidence. No source manifest, frontier implementation status, canonical
source plan or G2 gate changes result from this analysis. Normal R1 composition
still has 199 application and 34 bootloader imports.

[Machine evidence](goodix-gsensor-boundary-review.json) binds the locked image,
REA snapshot and controlled execution probe by hash. Physical accelerometer
behavior, arbitrary pointer aliases, concurrency and complete source/byte
identity remain unverified.

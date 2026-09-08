# UID receive-loop counter argument

The structure verifier pins eight instructions in each stock and candidate
receive loop, including instruction widths and branch destinations. It checks
252 decoded iterations spanning wrapped cursors, small and high-bit distances,
FIFO words and delayed readiness. This is a reviewed arithmetic argument tied
to decoded code, not a machine-checked proof or hardware validation.

Assume controller base A2000000, cursor c, end e, c != e, and each status poll
eventually observes bit 3. Both loops poll offset 28, read one FIFO word at
60, store its low byte at c, and increment c modulo 2^32. They compare the new
cursor with the unchanged end and repeat exactly when unequal. No other store
or helper occurs in the loop. Without eventual readiness both keep polling.

Let d = (e - c) modulo 2^32, with 1 <= d <= 2^32 - 1. After k stores the cursor
is (c + k) modulo 2^32. Equality with e first occurs at k = d: any earlier
positive k would require k = d modulo 2^32, impossible in that interval.
Thus the loop performs d stores, independently of the signed interpretation of
d. FIFO values may vary arbitrarily; each is narrowed to its low byte.

Decoded entry checks establish controller base and cursor/end distance before
consuming a receive-span event. The summary verifies the exact loop structure
again and supplies its exit register effects: cursor=end, r2=last FIFO word,
carry=false, and candidate r1=last ready status. Other registers are unchanged.
Decoded RX-empty call, helper clobbers and return then run normally. Fourteen
entry/exit cases cover small counts and four negative-capacity bit patterns,
with two register seeds and three last-word/status postcondition variants.
The 960 ordinary cases use complete traces rather than a summary.

This abstraction assumes accesses behave as modeled and do not alter stack,
code or controller semantics through destination aliasing. A huge negative
capacity cannot designate an ordinary valid RAM buffer on this target. The
argument preserves observed machine arithmetic; it does not establish safe
execution of such invalid calls, actual UID content, FIFO timing or board
runnability. No hardware operation is performed by these checks.

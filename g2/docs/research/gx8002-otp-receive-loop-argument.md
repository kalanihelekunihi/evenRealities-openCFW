# Receive-loop counter argument

Scope: the inner byte receive loop only. The structure verifier pins eight
stock instructions and seven candidate instructions, including widths and
branch destinations; it also runs252 decoded step cases. This is a reviewed
arithmetic argument tied to those instruction sequences, not a machine-checked
proof of the complete firmware function.

Assume controller base isA2000000, cursor=c, end=e, c!=e, and each poll eventually
observes status bit3. Both pinned loops repeatedly load28 and mask8 until set,
then load60 once and store its low byte at c. STBI.B increments c modulo2^32.
Both then compare the updated cursor to the unchanged end and repeat exactly
when unequal. There is no other write or helper in the pinned loop. Poll
failure to become ready leaves either loop polling indefinitely.

Let d=(e-c) mod2^32 in1..2^32-1. After k stores, the cursor is(c+k) mod2^32.
For0<k<d it cannot equal e: equality would require k=d modulo2^32, impossible
in that interval. At k=d it equals e and the loop exits. Thus the loop performs
exactly d byte stores, including when cursor arithmetic wraps. This count does
not assume d fits in a signed integer. Per-iteration FIFO read values may vary;
each is independently narrowed to one byte. The argument assumes those
addresses support the accesses; it does not validate actual RAM ranges.

For use in complete OTP-read qualification, decoded entry must establish the
same cursor/end difference and controller base; decoded exit must consume the
resulting register state and complete cleanup/return correctly. Those checks
must still be connected explicitly. This document does not admit the candidate.

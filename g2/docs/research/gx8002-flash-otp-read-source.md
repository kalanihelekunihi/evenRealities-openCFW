# OTP read wrapper candidate

Recovered runtime_gx8002_flash_otp_read.c from package0x15fb8/runtime10023fa4.
Native macOS-Os with priority allocator gives344/352 bytes. Compiled frame48
bytes(44 saved+4 local), stock52(44 saved+8 local). Not admitted; decoded frame
and effect qualification remains.

Initial descriptor reads and wrapped bounds follow OTP write: zero length
returns-1 after descriptor/flags; bounds or unsupported signed manufacturer
return-1. It computes base+offset+region*stride, waits ready, sets command0=48
and encodes address. Each iteration uses MIN.S32(remaining,32), preserving
high-bit lengths rather than treating them as ordinary unsigned32-byte chunks.

For a nonzero chunk it snapshots width, waits idle, then ordered controller
setup8=0,external A0300090=2,4c=0,10=0,0=407,4=width+1,18=0,f4=0,8=1.
It polls28&2 and sends width+2 bytes from the command buffer, including the
dummy byte. Then10=1,TX-empty,8=0,10=0,0=807,4=chunk-1,18=0,54=7,4c=1,8=1,
10=1,60=0. It polls28&8 for each byte read from60 into the destination, then
RX-empty,8=0,4c=0,external=3 then1,8=1. Address/remaining/buffer/count advance
and address is encoded again even after the final chunk. Final wait returns
count. Helpers' return values are ignored.

Width addition wraps; prefix count uses unsigned less-than, not a fixed
normal width. Synthetic huge counts/buffers are not physical-validity claims.
Every helper, MMIO, byte transfer, boundary, frame and return behavior still
needs decoded comparison. No hardware operation was performed.

Prepared model_gx8002_flash_otp_read.py with ordered MMIO, prefix bytes,
receive words/byte stores, polls and helper events. Encoders alternate width
so each chunk must reload it; the final encoder call remains explicit.
Three model tests pass: zero short circuit,33-byte split with width reloads/
wrapped destination/final encode, and rejection of huge signed chunks by the
finite trace generator. This model has not yet been compared to decoded code.
Large signed chunk and oversized prefix domains require separate treatment;
finite trace bounds must not be confused with firmware bounds or correctness.

Initial decoded stock/source comparison passes96 cases: four offsets,
six lengths around32-byte boundaries, supported/unsupported manufacturers,
and immediate/two-stall FIFO schedules. Models changing width, exact command
prefix reads, MMIO sequence, returned receive bytes and final encode. The
executor accounts for separate52-byte stock and48-byte candidate frames and
private stack words, plus helper clobbers and saved-register restoration.
This is initial coverage only; larger boundary/width/flag domains, huge signed
chunks and rejection tests remain before admission.

OTP read comparison expanded to2592 cases with both supported manufacturers,
high flags, wrapped base/stride and width, two polling schedules and clobber
seeds. Nine model/rejection tests pass, including missing local stack space,
wrong helper, extra byte/missing effect and unknown opcode. Huge signed chunks
remain outside finite trace generation; not admitted pending separate coverage.

Added eight decoded signed-chunk checkpoints for lengths80000000,80000001,
ffffff00,ffffffff with two clobber seeds and wrapped accepted bounds. Both
streams select the full high-bit length, not32. Candidate loads width just
before MIN.S32 while stock loads it afterward; checkpoint accounts for that
extra already-consumed read. The existing2592 full trace cases still pass.
These checkpoints only prove entry/selection; they do not simulate billions
of FIFO/byte operations or establish complete huge-transfer equivalence.
That remaining loop/exit qualification is required before admission.

Isolated receive-loop step checker now passes252 cases over six cursors,
seven unsigned remaining distances including high-bit values, three FIFO words
and two readiness schedules. Explicit precondition cursor!=end. It verifies
one read/store, modulo32 cursor increment, branch outcome and other-register
preservation. Stock loop body starts160f2 then branches through comparison1609c;
source body10024084 compares at its tail. An initial checker stop at the stock
comparison entry was too early and was corrected to stop after the comparison
returns to the body or exits. Full huge-transfer entry/cleanup plus induction
connection remain; this isolated step evidence alone is not admission.

Connected receive-loop summary to decoded entry/cleanup for fourteen cases:
lengths1/32/33 and80000000/80000001/ffffff00/ffffffff, two clobber seeds, wrapped
accepted bounds. The optional summary first requires exact pinned loop
structure, nonzero cursor/end distance and controller baseA2000000. It consumes
an explicit receive-span event and advances cursor to end under the reviewed
modulo argument, then resumes real decoded cleanup, address encode and return.
2592 full traces and eight signed-chunk checkpoints continue to pass. These
are compositional checks, not individual execution of billions of accesses.
Summary-specific rejection tests and scratch-register postcondition review
remain before admission. Physical buffer validity is still not established.

Summary postconditions now varied across three FIFO-word/status pairs for all
fourteen entry/cleanup cases. All pass;2592 full traces/eight chunk checkpoints
remain passing. Explicit readiness-bit precondition added. Five summary tests
reject changed stores, changed loop branches, missing comparison, empty-step
precondition and absent readiness. Cleanup checks use actual decoded code;
summary sets only the pinned loop's changed cursor/scratch registers and false
comparison result. Full firmware/hardware validity remains outside these checks.

Prepared reviewed admission adapter. It reruns full comparison and252 loop
steps, pins the reviewed counter-argument document hash and carries explicit
compositional/hardware/prefix-domain limitations. Fourteen focused tests pass.
Registered344-byte candidate for full codec integration. The candidate's48-byte
frame is smaller than stock52; decoded helper frames and private stack access
are checked separately. Package completion awaits integration and full artifact
verification. No physical OTP read/write was performed.

OTP read fully integrated:238 tests pass; macOS package build/verify-artifacts
pass.117 functions/133 code occurrences/16 data regions;8044 C,2040 data,80
metadata,322 fill,315606 retained. Codec SHA:
002ff61b09074547584386a2ddb6f46ee2ab17f7b88b0bcbbbdbbad5278fb0c2.
Package SHA:faa96c088ea31e15bc22f0e89f674505e9ca2dea9039d4a5598ee9a595dfa3dd.
Candidate pin does not imply vendor identity or physical qualification.
Full source-only goal remains active.

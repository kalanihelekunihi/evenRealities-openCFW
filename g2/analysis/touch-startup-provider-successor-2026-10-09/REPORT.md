# Touch constructor, CRT and halt source attribution

## New result

Genuine pinned source produces **100 distinct stock bytes**, independent-review
pending: constructor72 at[A9E4,AA2C), `_init`12 at[AA44,AA50), `_fini`12
at[AA50,AA5C), and halt4 at[AA40,AA44). These do not overlap reviewed exit,
memset or memcpy. No campaign/source-completion counters were changed.

The previously reviewed focused runtime subtotal is822bytes; these100bytes
are a separate unreviewed addition, not an admitted922byte total. Selected
PDLcensus remains54/54and4952bytes. Signed division, memset and exit independent
review passed per SIGNED-MEMSET-REVIEW.md and EXIT-REVIEW.md.

## Why the constructor comparison changed

The original client's nano-header compile emitted68bytes and retained37raw
non-relocated differing positions in
`../touch-newlib14-startup-exit-2026-10-09/results.json`. It is unchanged.

Pinned newlib configure.host defaults `have_init_fini=yes` at71 and appends
`-D_HAVE_INIT_FINI` at952–953; the Arm target does not disable it. This is an
authentic library-build definition, absent from installed client newlib.h.
One configuration-supported rebuild with that definition emits72bytes and
matches the raw nano archive member `libc_a-init.o`, including relocation fields.
Real GNU linking resolves `_init` to the genuine assembled CRT atAA44 and the
four literal bounds to stock values. Every linked byte matches stock.
`results.json` records source/generated-header hashes, commands, provider checks
and linker outputs. No flag sweep or source modification occurred.

## CRT is a real concatenated section

Pinned GCC crti.S emits the Thumb save frame and crtn.S emits its complement:
save r3/r4–r7/LR, then restore r3/r4–r7, recover LR through r3 and return.
The assembler supplies the observed alignment NOP. Real linker concatenation
produces12byte `.init` and12byte `.fini` sections matching stock and installed
CRT section bytes. Historical `init stub` terminology is superseded by this
concrete provider attribution; no handwritten stub was used.

## Halt configuration and preserved negative evidence

Source libgloss/libnosys/_exit.c contains arithmetic intended by its comment
to cause an exception, followed by an infinite loop. Actual optimized stock
contains only an infinite branch plus alignment NOP. Do not export that comment
as stock physical behavior.

The first authentic configure attempt failed because the minimal container
could not locate its archiver; its log/command/result remain preserved. Supplying
the pinned AR/RANLIB/NM succeeds. The unchanged configure/config.status generates
real config.h; no fake build header is introduced. The first size-optimized
provider rebuild emits2bytes `fee7`, and remains recorded as not matching the
4byte stock extent in halt-results-attempt2.json.

Pinned configure lines4080/4086 independently establish GNU default `-g -O2`
or `-O2`. One default-supported comparator retaining the independently observed
archive section layout emits4bytes `fee7c046`, exactly matching installed
libnosys.a `_exit.o` and stock. halt-default-results.json pins commands, header,
source, archive/member and outputs. This identifies a focused provider; the
complete original vendor configure/build/debug command is still not authenticated.

## Bounded instruction composition

56original/rebuilt instruction pairs PASS in original-results.json:
eight register seeds each for constructor, `_init`, `_fini`; four statuses,
optional stdio handler and four seeds for exit. Constructor executes the real
CRT before the single supplied init-array callback. Exit skips undefined weak
exitprocs, optionally invokes the supplied stdio callback, preserves the original
status into genuine rebuilt halt and executes four infinite-loop branches.
Callee-saved registers, SP, stack writes and event order agree. Preliminary
results using stock halt remain in original-results-before-halt.json.

Callbacks are explicit simple RAM instructions, not actual firmware callback
contents. These tests prove neither full reset reachability nor physical state,
scheduling, operating-system exit or whole-program destructor completion.

## Remaining finite dependencies

Static reset body3464..34B6 calls constructor at34A6, application3CB4 at34AE,
then exit at34B2 if that application returns. Whether it returns in actual use
is not established. Reset clears BSS[200008A8,20000F58), which includes the
stdio-handler slot20000F54. Thus that slot starts zero if this reset path runs
as recovered and is not subsequently written; later writers/live content remain
unmapped. Preinit bounds coincide at2000087C; init has one word at2000087C.
An occurrence of3435 at flash B948 is only a candidate frame_dummy initializer;
it is not a proven flash-to-RAM load mapping. Confirm the initializer copy/profile
and GCC crtbegin/crtstuff attribution before composing actual constructor
callbacks or finalizers. Existing historical startup recovery should be reused.

No Git, production, device, canonical ledger or shared campaign edits. Source
notices retained; exact GCC COPYING3/COPYING.RUNTIME and newlib COPYING.NEWLIB
are already preserved in adjacent pinned acquisitions. Missing source or runtime
evidence here is not a global source-exhaustion claim.

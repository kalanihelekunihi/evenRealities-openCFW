# Board eight-pin setup reconstruction

The function at package 0xfda8..0xfe2c / runtime 0x1020681c is now represented
by runtime_gx8002_board_pin_setup.c. Native macOS C-SKY GCC emits 132 bytes,
exactly the stock envelope and payload SHA-256
3fd7513b1f81793ebcdb3cc54c50c04714bcacc3751fadc11f5f43ebb7423e33.
The linked provider is compiled solely from C; stock is a comparison input.

Calls occur in order: pins 5, 6, 11, 12 with function 0, then pins 7, 8, 9, 10
with function 3. All eight run, and their return values are added modulo 2^32.
A zero sum returns normally. A nonzero sum calls padmux_set for pins 5, 6, 11,
12 with function 0, prints the diagnostic at 0x1020ad66, then branches forever.
The infinite loop is the recovered stock fatal path, not a placeholder for
unreconstructed functionality. This source is unregistered and unadmitted.

Next work must qualify decoded call sequences, return accumulation, ABI and
both terminal paths, compose actual guard/setter behavior, and reconstruct the
fatal diagnostic as source data. Exact compiled bytes are evidence of the
bounded function implementation, not whole-board or firmware completion.

Eight-pin setup decoded comparison now passes 3,096 cases and four tests on
macOS. All 256 combinations of zero/-1 guard returns are covered, plus two
unsigned wraparound cases, varying cleanup/printf returns, and both terminal
paths. Mutation testing detects a wrong configured pin. Actual helper bodies
and fatal diagnostic source remain pending; this caller is not registered.
Board-pin integration remains the existing live process; full goal is active.

Fatal setup diagnostic now compiles from a C string and matches its 49-byte
stock extent at 0x142f2. Seven setup/data tests pass. Decoded setup/guard
composition passes 2,048 combinations: both stock/source choices, initialization
states and all 256 conflict masks. Guard padmux/printf and setup cleanup
helpers remain modeled in this composition, with separate checked frames.
The setup caller is unregistered; board-pin integration remains live and the
full source-only goal remains active.

Fatal cleanup now executes decoded setters in 48 setup/setter combinations
with shared register words. Exact ordered writes clear pins 5,6,11,12 while
preserving neighboring fields, regardless of modeled checker failure. Nine
setup/data tests pass, including hook-controlled guard failure and cleanup
call gating. Actual checker/guard/diagnostic composition remains pending.
Integration session 1482 was confirmed live this turn; full goal stays active.

Cleanup composition now includes decoded checker and getter bodies: 192
stock/source combinations pass with written and inverted readback. Shared
cleanup words retain neighboring fields and ordered writes. Nine setup/data
tests pass. Guard/printf are still modeled in this cleanup-specific harness;
separate frames and scripted readback are explicit limitations. Integration
session 1482 was confirmed live; full source-only goal remains active.

Fatal printf forwarding passes 24 stock/source combinations, including
success suppression and loop entry after varied printf returns. Nine setup/data
tests pass. Formatter/output composition for this diagnostic remains pending.

Fatal setup diagnostic now passes four stock/source formatter/putf paths
through decoded fputc, console, UART wrappers and both transmitters under
scripted busy/ready MMIO. Literal text rejects unexpected integer/padding
helper calls; output exactly preserves its internal CR/LF and trailing text.
The 24 setup/printf cases and nine setup/data tests pass on macOS.
Shared whole-call stack and physical hardware remain unqualified; admission
of the setup caller remains pending and the full source-only goal is active.

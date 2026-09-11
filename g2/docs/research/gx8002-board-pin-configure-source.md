# Board pin configuration guard

The stock routine occupies package 0xfd68..0xfda8, runtime 0x102067dc.
The recovered C builds with native macOS C-SKY GCC to 64 bytes, exactly the
original envelope. It is not registered or admitted into firmware.

The routine reads the initialization flag at 0x20027b4c. Before initialization,
it checks the existing pin function through padmux_check: expected function 0
for pin 2, otherwise 1. A nonzero check result prints the diagnostic at
0x1020ad4a ("pin %d function conflict !\n") and returns -1. If already
initialized, the check is skipped. On success it calls padmux_set with the
original requested pin/function, ignores its result and returns zero.

The following board initialization routine writes this flag to one only after
its pin setup sequence. The flag's full lifecycle and concurrent access are not
yet established. The SDK driver helpers are already reconstructed separately;
no matching source or object for this board guard was found in the local pinned
SDK during the targeted diagnostic-string search.

Next qualification must compare decoded stock and C transactions, helper calls,
caller clobbers and preserved registers, including pin 2, invalid signed pins,
nonzero initialization values, setter failures, and printf return variation.
The diagnostic must become source-authored data and compositions must exercise
the reviewed padmux and formatter implementations. Build fit alone is not proof.

Decoded comparison now passes 8,100 stock/source cases covering boundary pins,
requested functions, initialization values and independent check/set/printf
returns. Seven tests pass on macOS, including mutations of the helper target,
pin-2 default selection and unsaved register preservation. The interpreter
models the decoded 12-byte saved-register frame and caller clobbers; it rejects
unsupported instructions. This is finite behavioral evidence with helper
returns modeled, not helper-body or physical hardware qualification. Run
`PYTHONPATH=tools python3 -m unittest tests.test_gx8002_board_pin_configure`
from g2. Source admission remains false.

The diagnostic is now source-authored in runtime_gx8002_board_pin_error.c.
Its compiler-generated data matches the exact stock extent at package 0x142d6,
including the signed decimal conversion, newline and NUL. Three data tests
pass (10 combined with the guard tests). Eighteen decoded formatter cases
cover stock/source implementations across nine pin values including INT_MIN
and -1. Integer conversion, character and padding helper bodies are modeled
by this formatter harness, so the report explicitly leaves those compositions
and physical UART pending. Neither the diagnostic nor guard is registered.

Guard/padmux composition now passes 3,360 cases across all 16 stock/source
combinations of guard, setter, checker and getter. The checker consumes the
decoded getter return and the setter checker consumes the written register
value. Initialization bypass, conflict rejection, pin 32, invalid signed pins,
and ignored setter failure are covered. Twelve guard/data tests pass, including
hook override and original-argument forwarding checks. Helpers retain separate
checked frames; shared nested stack, concurrency and physical pads remain
outside this finite proof. Printf wrapper/integer-body composition and aggregate
source admission remain pending.

Board guard/printf forwarding now passes 288 decoded cases with both stock
and source wrappers, signed pin boundaries, initialization/error paths and
varied formatter returns. Thirteen guard/data tests pass on macOS. The wrapper
forwards the original pin value and the guard preserves its -1 error return.
Frames and format-pointer translation are explicit harness boundaries; integer
and output helper bodies remain modeled. Candidate remains unregistered and
the full source-only goal remains active.

Diagnostic integer conversion now executes decoded stock/source ui2a bodies
at the formatter boundary. All 36 formatter/integer combinations pass for
nine signed pin boundaries, including INT_MIN and -1. The formatter interpreter
fork adds an explicit hook while preserving existing registered verifiers.
Helper memory/output-buffer translation remains separate; character/padding
and physical UART remain modeled. The 288 guard/printf cases and 13 tests
still pass. Source admission and complete source-only firmware remain pending.

Diagnostic padding now executes decoded putchw with the formatter-provided
width, sign, base and converted digits. Seventy-two formatter/integer/padding
stock/source combinations pass across nine signed pin values; the 288
guard/printf cases remain passing. Separate helper memory and output-stream
translation remain explicit. Character output and physical UART are modeled.
No integration admission yet; the full source-only goal remains active.

Added decoded putf boundary verification: 210 stock/source cases establish
character/stream forwarding and failure only for fputc result 0xffffffff.
Three wrapper tests pass, 16 combined with board guard/data tests. This helper
still needs connection to formatter/padding execution; fputc and physical UART
are modeled. No new provider admission; full source-only goal remains active.

Decoded putf is now connected to both literal character emission and padding
output. All 144 stock/source formatter/integer/padding/putf combinations pass,
including equality of the emitted byte stream with the expected diagnostic.
Separate frames and buffer translation remain explicit; fputc return and
physical UART are modeled. Candidate is still unregistered; full source-only
firmware remains the active objective.

Decoded fputc now passes 108 forwarding/return cases and is connected to the
diagnostic putf path using matched stock/source wrappers. It ignores stream
and console result and returns zero. All 144 diagnostic combinations and
16 tests pass. Console output remains a modeled boundary; physical UART and
full source-only integration remain incomplete. Goal stays active.

Console/UART port wrapper composition passes 72 decoded combinations,
including selected-port reads, descriptor arithmetic, byte truncation and
CR-before-LF behavior. Two new console tests pass, 18 combined boundary/guard
tests. This composition is not yet connected to the diagnostic; UART transmit
and the port-global value remain modeled. Full source-only goal stays active.

Diagnostic composition now reaches console/UART port wrappers and compares
the CR/LF-translated transmit sequence. Each transmit call also executes both
stock/source transmitter bodies with scripted busy-then-ready MMIO and exact
read/write trace checks. All 144 diagnostic combinations and 18 tests pass.
This uses selected port zero, separate frames and scripted MMIO; physical
timing/hardware remain unqualified. Aggregate admission/integration is next;
the complete source-only goal remains active.

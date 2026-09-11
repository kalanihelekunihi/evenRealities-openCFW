# RTC driver reconstruction

Stock package fc0c..fc90 matches the layout of the pinned SDK dw_rtc.o driver:
interrupt handler, start tick, set tick, and initialization. The SDK base-address
header identifies 0xa0003000 as RTC. Object identity is authenticated at commit
8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, blob
bc29abc7e65c826c8e5a2cd0799988445b5d50ff, SHA
 e2aad98d9d1e7a758e28952e3aef1e43c7edc0362dd6ac569ebe37fb8e64cd59.
Object relocation attribution remains pending; no object bytes are linked.

The reconstructed start-tick C reads register 0xa000300c and writes its value
OR 4. Native macOS compilation produces 16 bytes in the 16-byte region at
package fc2c/runtime102066a0. Set-tick writes its 32-bit argument to register
0xa0003008, producing 12 bytes at fc3c/runtime102066b0, identical to stock.
These primitives are unregistered and require decoded MMIO/ABI qualification.
Hardware timing and actual RTC behavior remain unqualified.

The interrupt routine at fc0c reads callback/argument storage at20027b40/44,
optionally invokes the callback, and reads RTC+18 afterward. Initialization at
fc48 enables clock module0, sets control bit4, queries the clock rate, checks
it against65536, writes RTC+20, installs IRQ4, and starts ticks. These bodies
are not reconstructed yet; exact callback/return and failure semantics require
qualification before admission.

Decoded RTC tick verification passes 644 stock/C cases spanning low-byte
values, all-zero/all-one words, walking ones and walking zeros. It checks exact
MMIO addresses, read/write trace, and leaf ABI preservation. Four focused tests
cover bit preservation, write-only set behavior, wrong-bit mutation and wrong
base address. Evidence pinning and admission export remain pending; the
primitives are still unregistered and physical timing is unqualified.

The RTC ISR is now reconstructed in C. It reads the registered callback, loads
its argument only when non-null, invokes it with the incoming IRQ, reads
0xa0003018 after the callback, and returns the callback result (zero if absent).
The initial GCC build duplicated the acknowledgement/return path due to shrink
wrapping and occupied 36 bytes. Candidate-local -fno-shrink-wrap produces the
original 32-byte layout, exactly matching the stock region at fc0c/runtime10206680.
SHA bb8cc0ade6891953872ceac15f1136faeccead9c79c3cb6b063768ee19f1d6c6.
Decoded callback/ABI and acknowledgement ordering tests remain pending; the ISR
is unregistered. Matching bytes do not establish physical RTC qualification.

RTC ISR decoded qualification passes 540 cases across absent/present callbacks,
IRQ values, argument pointers, callback results and acknowledgement words. The
trace checks callback-state reads, original IRQ/registered argument, callback
before acknowledgement, return-value preservation, caller clobbers and four-byte
frame/ABI. Four focused tests pass, including wrong callback-register and wrong
acknowledgement-address mutations. Callback bodies and physical acknowledgement
effects remain modeled/unqualified; admission pins/export are pending.

The RTC ISR admission verifier now pins its builder/verifier, exports a placement
row and linked artifact, and reruns all540decoded cases. Separately,
analyze_gx8002_rtc_primitives.py authenticates and relocates the SDK ISR/start/set
sections at their runtime addresses with BSS at20027b40. All three complete
sections match stock exactly. The SDK ELF is comparison-only and is never a
firmware input. ISR source admission remains bounded by the documented modeled
callback contract; it is unregistered pending the padmux integration.

All three RTC primitives now have integration-ready admission reports. ISR
qualification includes and pins full SDK attribution; start/set wrappers export
individual placement rows/artifacts and pin the common decoder, both builders,
attribution analyzer and wrapper. All qualification runs and eight focused tests
pass. The routines remain unregistered until the active padmux build completes.

RTC initialization is now reconstructed in C at fc48/runtime102066bc, compiling
natively on macOS to72bytes within72. It enables module0, sets control bit4,
queries module0 frequency, and rejects rates>=65536 by printing the exact
prescaler diagnostic. The failure path does not undo the prior enable/control
write. Success writes frequency toRTC+20, requestsIRQ4 with the recovered ISR
and null argument, and starts ticks. Compiler output uses an equivalent unsigned
65535 comparison; decoded boundary/helper-order/ABI qualification remains pending.
The diagnostic is separately source-authored in runtime_gx8002_rtc_error.c; its
placement qualification remains pending. Candidate SHA
11777e797c3c28ba130d614ea61f7cc19ce41c7e7283381f300bf9a4b94f191d.

RTC initialization decoded verification passes660cases across clock-rate
boundaries and control-bit patterns. It checks exact clock/control/frequency/
IRQ/start or diagnostic sequencing, caller clobbers and eight-byte frame/ABI.
Fourfocusedtests pass. Zero frequency is accepted as in stock; >=65536 rejects
without undoing preceding state changes. Helper bodies remain modeled, so
composition and diagnostic placement are still required before admission.

Decoded init/start composition passes60scenarios across stock/C outer and leaf
routines, frequency boundaries and control words. Successful start reads the
control value after initialization setbit4 and addsbit2; the error path skips
start entirely. Sixinitializer tests pass after adding a start hook. Other
helpers remain modeled without intervening control mutation; the separate
helper-stack and physical behavior limitations still apply.

Fresh ISR/start/set/diagnostic admission reports reproduce exactly. These three
C routines and the22-byte diagnostic are now registered in the experimental
source candidate. The732-test integration build is running. Initializer remains
unregistered pending additional helper qualification. No new package completion
is claimed until integration, packaging and artifact checks finish.

RTC init/clock-gate decoded composition passes60scenarios/60gatecalls across
stock/C selections, clock frequencies and source-register patterns. The gate
request is module0/enable1 even on the later frequency-error path; helper writes
stay within clock-control registers. Seveninitializer tests pass. Gate lookup
and helper stack retain their documented abstractions; frequency/IRQ/printf
bodies still require further qualification at the initializer boundary.

RTC/clock composition passes 12 cases with decoded source clock, lookup and
divider execution driving stock/source RTC initialization. Actual RTC clock
records select 12.288 MHz, 32 kHz or 24.576 MHz, exercising both diagnostic
rejection and prescaler/IRQ/start success. RTC and clock frames remain separate;
gate/IRQ/printf/start remain modeled in this check. Existing clock ELF inputs
were used without changing the running integration build's registered sources.

Nine RTC initializer tests now pass, including two frequency-hook regression
cases. They verify that the decoded helper's result overrides the placeholder
frequency in both directions: 32 kHz enables initialization, while 65536 rejects
it. This guards the RTC/clock composition boundary without altering registered
clock integration inputs. The initializer remains unadmitted.

RTC IRQ composition passes 24 stock/source outer and IRQ-helper combinations.
Successful initialization writes the RTC handler/private pair to the actual
IRQ-4 slots and executes the decoded controller-enable leaf, writing bit 4 to
0xe000e100. Frequency rejection produces none of those effects. Frames remain
separate and other helpers are modeled; physical interrupt delivery is not
proven. Existing IRQ artifacts were read without rebuilding registered inputs.

The actual source-built RTC diagnostic passes decoded stock/source formatting:
both emit exactly `RTC prescaler error!` plus newline and agree on the formatter
return. The check reads existing artifacts only. Character output remains
modeled; printf-wrapper composition and physical UART delivery are not claimed.

RTC diagnostic/printf composition passes 24 stock/source outer and wrapper
combinations. It checks the real diagnostic pointer, decoded wrapper forwarding
with no variadic arguments, and the separately decoded formatter's exact output
and return. Success paths skip printf; failure emits once. Nine initializer tests
still pass. Harness pointer translation and separate frames are explicit; UART
hardware output is not proved. The initializer remains unadmitted.

The consolidated RTC initializer qualification now rebuilds/rechecks clock source,
authenticates upstream object attribution, runs the 660 core cases and gate,
start, clock, IRQ and printf compositions, and exports the 72-byte initializer
ELF. The aggregate run passes on macOS with principal evidence hashes recorded.
It remains unregistered pending dependency/admission review; separate-helper
frames and physical delivery/timing limits remain explicit.

# ADC open native frame and delay binding

`adc/stock_named_adc.c` now places open's configuration in its native saved
R3 word at caller SP-24 through a ten-byte frame bridge. The C body keeps
the live lookup, initialization, channel setup and error-call sequence.
Missing and already-open paths retain incoming R3. Initialization copies
the typed SDK template word `0x00060001`, then replaces its low byte with
12-bit resolution, yielding `0x00060002`. The complete final word is
restored to R3, including callback changes.

Layout/enum assertions constrain the four-byte SDK configuration. Its
readonly C template matches the stock word at `0x9a5d4`. REA and raw
instructions agree on initialization and channel ordering: global init is
set after its error call, input selector is copied into channel config,
opened is set before the channel error call, and two delays follow.
Volatile state views preserve reloads and byte stores around callbacks.

Stock calls the six-byte decrement/branch delay at `0x9a5e0` twice with
`64000`. Its bytes match the existing `r1_rtt_delay_cycles` primitive exactly.
ADC open now calls that provider directly, replacing its dependency on
the unresolved microsecond wrapper. This does not resolve that wrapper's
other consumers or prove physical elapsed time.

The probe passes 9,217 stock/C comparisons. Cases vary opened triples,
initialization, all three device names and a miss, successful/error returns
from both SDK operations, and sixteen callback mutation modes. Actual ADC
adapter code executes; comparison, Nordic init/channel init, and returning
error handlers are modeled. Bulk delays are modeled at the native
boundary. One integrated comparison executes both actual six-byte delay
loops twice in native and source runs.

Checks compare callback order and owned arguments, configuration/channel
bytes, all ADC state, exact CPU writes to the saved word, R0/R3, callee-saved
registers, SP, masks and callback alignment. A controlled old-source replay
shows its configuration at SP-28 and final R3 `0xabc00003`, versus native
SP-24 and `0x00060002`. The repair matches the native pointer and word.

Close, registration, sample, operations and cold-state sections retain
exact bytes and relocation identities. The other 561 source units are
unchanged. All 562 R1 units compile without failures or duplicate strong
symbols. Eligibility and imports remain unchanged at 211 application /
34 bootloader, and `make sources-check` passes. Exact bindings are in
[the machine-readable review](adc-c-open-frame-review.json).

The C body is 146 bytes plus its ten-byte bridge versus 130 native
instruction bytes. Callback SP changes from caller SP-24 to SP-56 while
the configuration remains at SP-24. Physical SAADC/analog behavior,
elapsed delay, actual error recovery, private frames, arbitrary faults,
exceptions, concurrency, timing, final boot/linking, qualification and
whole-image byte identity remain unproven. No G2 gate or source-plan
selection changes.

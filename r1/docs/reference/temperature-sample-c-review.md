# R1 temperature sample collection, validation and publication in C

`native_temperature_sample.c` supplies the native callback at `0x4bc40`,
range check `0x4b598`, consistency check `0x4b560`, five-sample publisher
`0x4b4b0` and health-mode predicate `0x4c634`. The measurement callback now
resolves the periodic controller's remaining native dependency. Its frontier
routes reference these actual interfaces rather than the differently shaped
Gomore analysis-plan functions. [The review receipt](temperature-sample-c-review.json)
records production source/object hashes, REA byte evidence and replay results.

The callback increments the attempt byte modulo 256 and times out when the
incremented value exceeds 30. Otherwise it accepts sample halfwords from 30,000
through 50,000 inclusive. Every previously collected value must be within 300;
the native difference is narrowed to 16 bits before comparison. An inconsistent
sample clears the collection count. A consistent sample is stored at the live
count index, after which the count byte is read again, incremented modulo 256
and compared with 5. This preserves corrupt-index aliasing, including a store
that overwrites the count/attempt bytes themselves. No length or null policy is
added. Successful collection publishes before unregistering; timeout also
unregisters, and the timing handle is cleared after the unregister call.

Publication uses the first five samples whenever the count is at least five.
It truncates their mean to a halfword, then uses the stock binary64 constants
0.01 and 0.1 with truncating unsigned conversion. The first scaled value occupies
the low halfword of an otherwise zeroed eight-byte event-9 record. The second
is captured into the sleep record only when active equals 1 and its live index
is below 50. Event publication requires health mode exactly 2. The new unit owns
only the authenticated 106-byte cold-zero capture at `0x2001e3ea`, ending before
the adjacent system state. It reuses the prior timing-record and handle owners.
Startup RW/ZI replay with guards and independent RW decoding confirms those
106 initial bytes; no neighboring ownership is inferred.

`native_double_to_uint.c` adds a base-AAPCS compiler-helper bridge to the existing
`r1_binary64_to_unsigned32_bits` implementation. It does not duplicate the
conversion algorithm. Stock ignores the sign bit and retains Arm register-shift
behavior beyond the ordinary unsigned range; the standard saturating compiler-rt
conversion would differ. The explicit `pcs("aapcs")` preserves R0/R1 arguments
inside this hard-float image. Across 167,936 paired tests, return values match
stock for both signs, every exponent, varied significands, seeded random bits,
and both scaled results of every 16-bit average. Preserved registers, SP,
interrupt masks and FPSCR also agree. A compiled wrong-ABI bridge is rejected.

A further 2,956 paired cases execute the actual C sampling helpers and math
providers. They cover range/distance boundaries, attempt wrap and timeout,
corrupt collection counts, input/state aliases, logical null faults, batch
capture limits, changing logging modes and provider mutations. Another 144
paired scenarios execute periodic startup through actual C clear/getter/name
registration and then repeated callbacks: five-sample success, instability
reset and timeout. Event payloads, call arguments/order, provider-boundary and
final state, preserved registers, stack restoration and masks agree. Eight
compiled sampling defects are rejected, making nine negative controls overall.

Callback provider-call depth is 24 bytes for logging and unregister, and 48
bytes for nested publication, matching stock in these fixtures. Direct publisher
calls use 24 bytes on both sides. This does not establish private stack identity;
void return residue, caller-clobbered registers and flags are excluded. Event
publishing, unregister, logging, and lower object registration remain modeled
boundaries. Physical sensor behavior, concurrency and asynchronous delivery
are unverified.

All 622 units compile and both relocatable payloads compose without duplicate
strong symbols. All 620 prior objects are unchanged. Application imports fall
from 166 to 164, resolving the sample callback and `__aeabi_d2uiz` without adding
imports; bootloader imports remain 34. Exact qualification admits none of the
five new sampling bodies. The mechanical AEABI bridge is not an independently
qualified stock body. The canonical plan remains unchanged; a fresh hybrid
retains 4,295 source-built bytes and matches locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Complete source linking and instruction identity remain open.

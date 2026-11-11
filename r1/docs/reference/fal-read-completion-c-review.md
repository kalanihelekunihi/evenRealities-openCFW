# Complete FAL reads across the internal-flash length boundary

The stock FAL adapter discards device status and reports the requested count.
The registered internal-flash read policy loads only a 16-bit transfer length.
A request for 65,536 bytes therefore previously reported success while the
provider's byte-copy loop received zero. REA confirms both native bodies.

The C adapter now splits reads into requests of at most 65,535 bytes, advancing
the buffer and offset after each successful request. Any nonzero device status
returns `-1` immediately. A failed later chunk leaves the successful prefix
intact and the remaining destination untouched. Counts above `INT32_MAX` are
rejected because FAL's signed result cannot represent them. Zero-length reads
retain their single provider call. This intentionally improves stock behavior.

Verification includes 36 compatible native request/return comparisons with the
native device boundary modeled. Ten large reads execute the actual C adapter,
internal-flash policy and mapped-byte-copy loop through a controlled C dispatch
boundary; they cover 65,536 through 131,071 bytes with before/after callbacks
both enabled and disabled. Another 36 injected failures check stopping, copied
prefix and untouched suffix. Three actual uninitialized-provider cases and two
unrepresentable-count cases pass. Two compiled defects restoring length
truncation and ignored errors are rejected by runtime assertions.

All 852 units compile and both relocatable payloads compose. Only this read
function's allocated text section changes in its object; all 841 other
nongenerated objects and both import sets remain unchanged. R1 manifest
validation passes. Imports remain 66 application and 22 bootloader symbols.

This establishes controlled C behavior, not physical flash completion, final
linking or boot. The existing global request remains shared; concurrency,
arbitrary callback mutation, pointer corruption, buffer overlap and address-wrap
faults are outside the replay. Upper TSL/sector readers still ignore errors;
their coupled C conversion and iterator propagation remain open.

[Machine evidence](fal-read-completion-c-review.json) binds REA, source, probes,
negative controls and build reports by hash.

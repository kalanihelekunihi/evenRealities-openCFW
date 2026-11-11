# R1 RTC cached lookup and calendar/tick evidence

The existing lazy `sys rtc` lookup now participates in relocatable
composition. It reads the cache cell once, looks up only when null, stores
the result, and returns it. Failed null lookups are retried; a non-null result
is retained. Source and compiled object bytes are unchanged. All 243
three-call stock-versus-source sequences pass (729 invocations), including
lookup-result combinations and mutation of the cell during lookup. Tests
compare cell reads/writes, lookup name, provider-call SP, return sequences and
final cell. No extra volatile read was added where stock performs only one.

The native calendar kernel and RTC tick candidates were also checked before
considering further RTC integration. All 1,143 calendar vectors match the
eight native output words, covering deterministic random epochs and boundary
vectors across 1970–2106. All 300 tick cases match counter state, record bytes
and alarm-callback hours, covering divider thresholds, epoch wrap, signed
minute offsets, alarm matches/misses and controlled mutation of the second
field during a minute-field read. No body repair was justified by these tests.
Those lifecycle/device translation units were excluded at this review stage.
The later [device closure](rtc-device-closure.md) includes the checked device
unit. The subsequent [lifecycle review](rtc-lifecycle-review.md) includes its
checked C lifecycle/driver bridges; physical driver execution remains separate.
The later [snapshot review](rtc-snapshot-order-review.md) repairs a separate
divider-sampling order defect in that excluded device unit; its other
allocated sections and relocations remain unchanged.

## Century behavior is not Gregorian

At epoch `4107542400` (Gregorian 2100-03-01 00:00:00 UTC), stock reports
`tm_mday=29`, `tm_mon=1`, `tm_year=200`: February 29, 2100. The existing native
C candidate agrees. This kernel follows a four-year cycle and does not apply
the Gregorian century exception. Earlier contextual API/host-gmtime tests
must not be cited as native-equivalence proof at this boundary. The review
preserves observed stock behavior rather than changing the calendar policy.

REA observes the 20-byte cache body at `0x50DC0..0x50DD3`, the 138-byte
calendar body at `0x276C8..0x27751`, and 102 instruction bytes for tick at
`0x56274..0x562D9`, inclusive. The historical 108-byte tick extent includes
two padding bytes and a four-byte counter-address literal. This is recorded
without changing canonical ledgers or accepted pseudocode coverage.

All 562 R1 units compile and both compositions pass. One import resolves,
reducing application imports from 240 to 239; bootloader imports remain 34.
No new imports, duplicate strong symbols or source-plan entries were added.
The RTC peripheral, hardware interrupts, drift, complete fault state, private
stack contents, startup chain and exact source qualification remain open.

[rtc-cache-kernel-review.json](rtc-cache-kernel-review.json) binds unchanged
source/object hashes, report identities, test counts, the century vector and
REA observations. Probes remain under ignored `build/goal-r1-rtc/`.

# R1 RTC snapshot sampling-order repair

The existing C snapshot candidate now preserves the native order of memory
accesses: sample the epoch, publish it at output +44, sample the live 16-bit
divider, then publish the 32-bit wrapped `epoch * 1000 + divider` at +56
with a zero high word at +60. The epoch is captured once. Local volatile
views of the counter and output preserve the observed accesses without
changing their shared declarations or introducing assembly.

Previously Clang read the divider before publishing the epoch and wrote the
timestamp's high word before its low word. A controlled mutation at the
epoch store exposed 54 mismatches in 144 cases. The smallest example starts
with epoch/divider zero, then changes the divider to one at publication:
stock returns a timestamp of one, while the old candidate returned zero.
Epoch-only mutation did not expose the defect because that value was already
held by the compiled candidate. The repair therefore addresses the measured
divider ordering rather than assuming an epoch re-read.

All 144 corrected cases pass for complete output bytes, return status,
counter state and the combined ordered read/write trace. Cases include null
output, epoch and multiplication wraparound, divider values 0/7/65535 and
interleaved changes of both epoch and divider. Null output returns four
without accessing the counter. Unwritten output fields remain unchanged.
This preserves stock's two sampling points; it is not an atomic snapshot.

REA observes the 36-byte native body at `0x5639C..0x563BF`, inclusive. Its
pseudocode places an apparent epoch read above the null check; assembly starts
with the null branch, confirmed by access traces. Native instructions, not
that decompiler ordering, govern the comparison.

Every other allocated section and normalized relocation in the device object
is unchanged. All 562 R1 units compile and both compositions pass, with the
same 239 application and 34 bootloader imports at that stage. The device
provider was initially excluded; the later
[device closure](rtc-device-closure.md) checks its remaining operations and
includes it in composition. No source-plan selection,
accepted coverage or workflow gate changed. Exact instruction/timing identity,
complete fault state, live RTC interrupts and physical clock behavior remain
unverified.

[rtc-snapshot-order-review.json](rtc-snapshot-order-review.json) binds the
counterexample, before/after results, source/report hashes and REA evidence.
Probes and the neutral snapshot remain under ignored
`build/goal-r1-rtc-snapshot/`.

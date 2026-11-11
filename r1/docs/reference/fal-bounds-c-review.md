# Overflow-safe FAL partition ranges

Read, write and erase now reject `addr > limit` or `size > limit - addr`.
This avoids wrapping the old 32-bit `addr + size` check. The existing out-of-bounds
error and diagnostics remain, and rejection happens before lookup or driver
calls. Valid zero-length requests at the partition endpoint remain accepted.

REA and controlled stock execution confirm the old failure: offset
`0xfffffff0` plus 32 bytes wraps to 16, so each native function admits the
request against a 16-byte partition and reaches the driver. Each C function
now rejects it without lookup or driver activity. This is an intentional
improvement over stock behavior.

All 24,681 comparisons where admission agrees with stock pass, including
null assertions, exact endpoints, signed provider results, lookup failures,
field ordering and callback mutations. Another 2,895 C-only overflow-rejection
cases pass. Each operation includes 1,512 additional boundary/random cases;
the range oracle uses unbounded Python arithmetic. Three compiled variants
restoring the old guards are rejected.

All 852 units compile and both relocatable payloads compose. All 842
nongenerated objects, unrelated FAL function bodies, data bytes and import sets
remain unchanged. R1 manifest validation passes. Imports remain 66 application
and 22 bootloader symbols.

Lookup, final drivers and diagnostics are modeled. No physical flash access
occurs. Base-offset translation wrapping, corrupt metadata, concurrent mutation
and hardware geometry remain outside this fix. Full linking and boot remain
unverified. [Machine evidence](fal-bounds-c-review.json) binds source, REA,
probes, negative controls and normal build reports.

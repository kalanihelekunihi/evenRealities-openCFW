# C command routing into NV recovery

System command `0x0011` now points directly to the implemented four-argument C
NV envelope handler. This closes the unresolved planner-name import without
adding an alias implementation. The 35 command records retain their original
keys and reserved bytes; only the recovery callback relocation changes.

The shared lookup and all three module dispatchers now use ordinary C. A lookup
result carries the callback and native lower-search index explicitly, preserving
the callback's meaningful fourth argument without register bindings. Null packet
and ordinary miss results are retained. Below-minimum keys return zero before
unsigned index underflow can read before the table.

The link-ready query's assembly frame is also removed. Its C call forwards
exactly `(handle,17,1,1,0,NULL,0)` and returns whether the provider result is
nonzero. NV logging declarations now match the pinned SDK's void signatures;
empty-payload handling returns zero instead of an incidental logger value.

Verification passes:

- 2,721 stock/C module and lookup comparisons, covering all 166 native
  instruction bytes, all 35 command entries and the exact callback seed.
- 25 link-ready comparisons, covering all 32 bytes and seven send arguments.
- 288 complete C recovery-route cases through actual command tables, lookup,
  payload getter, envelope, command admission, CRC/merge, cached classes and
  memory routines. Payloads, dirty flags and unchanged bytes are checked.
- 6,378 existing touch-handler/module regressions with the new lookup.
- Five compiled defects changing the NV target, callback seed, underflow guard,
  query arguments and query result are rejected.

A controlled stock lookup reads `TABLE-8` and returns a phantom callback from
that seeded RAM. The C guard rejects the request; the phantom is never executed.
Four C-only cases check below-minimum lookup and module rejection.

All 855 units compile and both relocatable payloads compose. All 843 other
nongenerated objects remain unchanged. Application imports fall from 63 to 62;
bootloader imports remain 22. R1 manifest validation passes. No persistent state
or manifest entry is added.

Callbacks/services are modeled in the direct comparisons. In the complete C
route, unrelated handlers are unexecuted assertion stubs; logging and the report
backend are modeled. Packet available-length validation and the payload getter's
advertised-length behavior are unchanged. Tests supply complete readable buffers.
Physical flash/radio behavior, full linking and boot remain unverified.

[Machine evidence](nv-recovery-route-c-review.json) binds source, REA, normal
builds, replays and negative controls.

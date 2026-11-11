# Clock bootstrap in normal source composition

The existing `native_clock_bootstrap.c` now participates in normal linkage.
It supplies the clock constructor, default backend table/getter and
second-change callback needed by the manager's hardware startup path. All
of its dependencies are already source-owned. No assembly or alternate
implementation is added, and its compiled object is unchanged.

Earlier constructor work left this unit excluded pending callback validation.
The callback at stock `0x5a9d0` saves its incoming word, fetches the current
backend timestamp, compares the live cached epoch, and publishes event 4
with one byte from the incoming word only when they differ. The event payload
is not the newly read timestamp. The C implementation follows that behavior.

128 isolated stock/C callback pairs cover full incoming words, epoch and
cache values, equality/inequality, live cache mutation and both PRIMASK
settings. Another 1,152 pairs execute the actual timestamp thunk, default
getter, 64-byte RTC request, memory clear and registry dispatch. Only the
leaf RTC operation and event publisher are modeled. Zero/partial/full RTC
responses, ignored statuses, cache mutation, event data, returns to caller,
callee-saved registers, SP and masks are checked. Four compiled defects are
rejected: timestamp as payload, four-byte event length, suppression of zero
epochs, and reading the cache before the timestamp call.

The C callback uses a 16-byte frame; native uses eight. Payload pointers are
normalized by role. Private frame aliases, incidental restored R3, other
caller-clobbered values, void returns and exception identity are excluded.
This is an ordinary C callback ABI result, not native frame/byte identity.
No exact callback bytes are added to source qualification.

The actual current object also reruns all 4,400 constructor comparisons using
real snapshot/bind helpers. They cover exposed context/backend slot mutation,
raw registration flags, null/default configuration, configuration aliases,
absent callbacks, failed initialization and ordered state updates. The
recorded Clang constructor still has the tested 24-byte provider frame.
That profile-specific result does not transfer to arbitrary compilers.
REA windows authenticate both the constructor and callback against raw stock.

All 803 R1 units compile with no failures or duplicate strong symbols.
Application imports remain 69; one more existing object now participates.
All 801 nongenerated prior object hashes are unchanged, including bootstrap.
The two generated boot objects retain source hashes, allocated bytes and
relocations. The only manifest change enables bootstrap linkage. Strict
bootloader linking and R1 source checks pass. Global source checking retains
the unrelated unlisted G2 `resident_rom_thumb_set.S` failure.

Physical RTC behavior, asynchronous timing, the remaining manager startup
providers, full application final linking and boot remain unverified. No
source-plan selections change. The [machine-readable review](clock-bootstrap-link-review.json)
records exact inputs, current execution, negative controls and scope.

# R1 stream and subscriber failure intrinsics

The BASEPRI writes in allocation-failure paths of `native_stream_bootstrap.c`,
`native_stream_poll.c`, `native_subscriber_registration.c` and
`native_stream_objects.c` now use `__builtin_arm_wsr("basepri", mask)` instead
of handwritten assembly. Their complete compiled objects are byte-identical
to the preceding build. [Machine receipt](runtime-intrinsics-c-review.json).

The normal R1 build passes all 607 units and both relocatable compositions
without failures or duplicate strong symbols. Every one of the 607 objects,
and both composition outputs, is identical to the previous report. Only those
four source files change; the manifest, import sets and canonical source plan
are unchanged. There remain 168 application imports and 34 bootloader imports.

RTT conversion probes were not adopted. Replacing its BASEPRI reads and writes
together, writes alone, or its read alone changed the object. In the writes-only
probe, `movs r0,#32` moved before `mrs r7,BASEPRI`. This observation does not prove
a functional error, but it loses the direct byte-preservation argument and
would need separate ABI, flags and ordering verification. The original RTT
source, including its register-capture boundaries, was restored and its source
hash rechecked against the preceding report.

These intrinsics are architecture- and compiler-specific C, verified with the
configured Clang toolchain. Object identity preserves prior behavior and its
existing proof limits; it does not establish stock instruction identity,
physical privilege/fault behavior or a complete source-only firmware image.
The four changed units have no canonical source-plan selections. The preceding
hybrid output and source-plan hash were read back and revalidated against the
locked application; redundant behavioral tests and a hybrid rebuild were not
needed for unchanged compiled objects.

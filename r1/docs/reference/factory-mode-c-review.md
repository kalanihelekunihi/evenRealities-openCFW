# R1 factory-mode activation in C

The stock activation routine at `0x48bd0` (116 code bytes) now has one C
candidate, `r1_factory_mode_start`, in `runtime/native_factory_mode.c`.
[Machine receipt](factory-mode-c-review.json).

The candidate owns the observed 28-byte state prefix at native address
`0x20006c34`. Executing the stock RW initializer over poisoned memory proves
its initial bytes, including `0xff` at offsets three and four; surrounding
initialization guards survive. Those bytes remain reserved without an invented
meaning. The existing Goodix selector reads the active byte at that native
fixed address. This step does not change that consumer; final source-link
placement and runtime aliasing remain unproven outside the controlled fixture.

A nonzero active byte returns immediately. Otherwise, a nonzero reset argument
reads the configuration byte, writes its value OR `0xc0`, clears the shared
configuration word, calls its setter with zero and reloads the shared word.
The alternate branch reads the configuration word and publishes that returned
value directly. Both paths save the selected configuration before setting
active to one. The input handle is ignored as stock does.

The current nonzero timer is released, then a new timer is requested with the
callback at `0x3cd24`, period 61,440 and context zero. Its returned handle is
stored even when zero. If the current accelerometer registration field is zero,
registration uses `acc`, group `factory`, callback `0x6f304`, argument one and
fifth stack argument zero. The aging field is reloaded afterward; a zero value
registers `aging` with callback `0x8156c` and the same remaining arguments.
Provider mutations and partial setup remain observable. These callback bodies
and registration semantics are separate dependencies, not inferred from names.

Verification passed 8,704 paired stock/C cases covering active-byte values,
full-width reset arguments, timer/registration presence and zero returns,
configuration values, interrupt masks, shared-state mutations and ordered
byte/word accesses. The five-argument registration call preserves its fifth
argument value. Five mutants were rejected: wrong active test, wrong byte mask,
ignoring the configuration reload, wrong timer period and reversed aging check.
Production replay passed again after the negative controls.

The C provider has a 24-byte frame versus stock's 16 bytes. A strict native-frame
check rejects it. Tested Clang O2/Oz/frame-pointer options and a GNU Arm 9 probe
also retain 24 bytes; GNU was not adopted or behavior-qualified here. Provider
frame identity, raw void return registers, private stack bytes and APSR remain
outside the behavior comparison. No physical exception or callback execution
is established by the modeled providers.

All 607 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. All preceding 606 objects remain
identical. Activation resolves, while six deeper imports become explicit:
two configuration writers, registration-by-name, and three callbacks. Existing
configuration getter dependencies also remain. There are now 168 application
imports and 34 bootloader imports.

The scoped qualifier admits no executable bytes, and the canonical source plan
is unchanged. The fresh hybrid matches the locked application using 4,271
source-built bytes, 641,889 executable pull-through bytes and 248 resource bytes.
Configuration access, timer operations and registration are modeled in this
replay; persistence, actual timer/stream integration, full source-only linking,
byte identity and physical factory-mode behavior remain unfinished.

The subsequent [name-based stream registration wrapper](stream-register-name-c-review.md)
supplies that import in C and exposes the deeper object-registration body.
Its factory caller-chain replay retains the documented activation frame gap.

The subsequent [factory threshold latch](threshold-latch-c-review.md) supplies
the `aging` callback in C and shares the existing mode-state owner through
`native_factory_mode.h`. The mode object's compiled bytes remain identical.
Motion and temperature callbacks and configuration persistence remain separate
unfinished dependencies.

The subsequent [motion event adapter](motion-adapter-c-review.md) supplies the
`acc` callback in C, sharing the existing active-state owner and owning only its
separate six-byte axis cache. Its legacy reply frame retains an eight-byte gap;
the sender and temperature callback remain unfinished dependencies.

The subsequent [temperature monitor and shutdown](factory-temperature-c-review.md)
supply the temperature callback, periodic counter persistence and mode teardown
in C. Sampling through the existing reducer is replayed, while shutdown retains
a frame gap and stream unregistration remains explicit.

# R1 GoMore sensor authorization in C

Follow-up: [HR/HRV adapters](gomore-hr-adapters-c-review.md) now resolve two
callbacks with the actual C authorization path tested. Counts below describe
the original dispatcher build.

`native_gomore_authorization.c` replaces stock `0x49410` (506 bytes) with C
sensor ownership, ordered stream registration/cleanup, callbacks and idle-timer
transitions. The [receipt](gomore-authorization-c-review.json) binds production
objects, the [native contract](gomore-authorization-native-analysis.md), startup
proofs, negative controls, qualification and normal composition.

A shared header and one state owner consolidate the former device-ID once-status
and wake-flag allocations. The 148-byte RW state at `0x20006da0` includes the
ready/once-status byte at **offset 0**, a separate cached-ID validity byte at +4,
stream/timer handles, HRV counters and seven 16-byte authorization entries.
Entry 4's flag remains at `0x20006e04`. The separate eight-byte ZI sample state
is at `0x2001a590`. The old two byte owners are removed; net new owned storage
is 154 bytes, total shared storage 156 bytes. Native RW/ZI startup handlers and
an independent RW decoder match all initializer bytes, with surrounding guards
unchanged. The existing device-ID command, record-change detector and wake
callback use these shared fields.

Consumer instruction review corrected an earlier analysis mapping: the literal
at `0x6c5c8` is `0x20006da0`, and the change detector reads that byte directly.
`0x6ab88` separately reads cached-ID validity at +4. The header and native
analysis receipt now distinguish them. No duplicate status/table copy remains.

C preserves full-word enable equality, the low-bit-only update, and the enable
callback before that update. Disable updates the bit before checking live
sensor users and fresh handles. Unregister precedes late handle/HR/HRV clears.
Later sensor checks reload the entry flag after intervening providers. All
sensor-user predicates read each visited flag once, and the idle predicate is
called again on the native non-create path. Timer creation uses the actual
three-argument interface; decompiler extra arguments are not forwarded.

**2,026 paired stock/C/oracle cases** pass. Native dispatcher/predicates and
compiled C dispatcher/helpers execute, while registration/unregister, timer,
user callback and log providers are modeled. Cases include invalid indices,
non-boolean enables, shared users, callback/provider changes to the current and
other entries, handle/timer mutations and changing log modes. Return values,
exact observed call/state order, final SRAM/guards, preserved registers, SP,
masks and FPSCR match with a warmed FPU. Private stack, caller-clobbered state,
concurrent execution and first-use FP activation remain outside this proof.

The shared status consumers pass **5,376 paired native/C record-change cases**
and **512 compiled status get/clear cases**, checking all 256 status values and
all neighboring state bytes. The wake consumer passes **1,104 paired cases**
using the shared flag address; authorization remains modeled in that caller
fixture. Ten compiled defects are rejected, including normalized enables,
early flag changes, cached later flags, wrong cleanup widths and timer logic.

All **673 units** compile with no duplicate strong symbols; **669 prior
source/object pairs** are unchanged and the three shared consumers are the only
changed prior units. Application imports become **167** and bootloader imports
remain **34**. Replacing the authorization import exposes five native callbacks:
accelerometer, raw-HR, HR, HRV and idle-timer adapters. These are remaining ABI
reconstruction dependencies; the provider-rich frozen GoMore functions are
not substituted for them.

No body qualifies as instruction-exact. The canonical plan remains at **4,369
source-built bytes** and the fresh hybrid matches the locked application via
executable pull-through. Physical sensors, full source-only linking, whole-image
state placement and byte identity remain unproven.

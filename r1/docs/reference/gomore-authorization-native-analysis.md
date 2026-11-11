# R1 GoMore sensor authorization contract

Stock `0x49410` (506 code bytes) manages shared sensor subscriptions and an idle
timer. The [receipt](gomore-authorization-native-analysis.json) binds REA
pseudocode and raw bytes to the locked artifact, native startup checks and an
independent state/call oracle. **1,900 native/oracle cases pass**. The [C implementation](gomore-authorization-c-review.md) now follows this
contract; counts below describe the preceding native-only analysis.

The 148-byte state at `0x20006da0` contains the shared ready/device-ID once-status byte 0, cached-device-ID valid byte 4,
four stream handles at offsets 8/12/16/20, idle timer at 24, HRV counters at
28/32 and seven 16-byte authorization entries at offset 36. Each entry has a
flag byte, enable callback word at +4 and disable callback word at +8. Native
startup RW expansion and an independent decoder agree: flags are
`2,30,30,2,4,12,0`; callback words and the remaining state are zero. The eight
bytes at `0x2001a590` start zero in the native ZI region.

Two bytes already have C owners: `r1_device_id_once_status` at `0x20006da0` and
`r1_gomore_wake_authorization_flags` at `0x20006e04` (entry 4). A C dispatcher
must share these fields, not allocate a second table or state copy. Consolidating
ownership must preserve their users and the existing cold-value proofs.

The ready check precedes index validation and logs when unset. Indices above 6
return zero. Equality compares the stored bit zero to the **full input word**;
non-boolean enable values therefore retain the native behavior. Nonzero enable
checks bits 2/4/8/16 in order for `acc`, `raw_hr`, `hr`, `hrv`. Each native
predicate scans all seven entries for an enabled user of that sensor. If no
user exists and the corresponding handle is zero, registration runs with owner
`gomore`, mode 1, context 0 and stock callbacks `0x6b115`, `0x6b229`, `0x6b1b9`,
`0x6b1f5`. The enable callback runs before the fresh flag-byte low-bit update.

Disable updates bit zero first, then rechecks each sensor's current users and
fresh handle. Unregister runs before clearing the handle. HR additionally
clears the word at `0x2001a594`; HRV clears state words 28/32 and only the byte at
`0x2001a590`. The disable callback runs afterward. Provider mutations can change
later flag/handle decisions, so entry bytes and handles must remain live reads.

The idle predicate at `0x6ad04` returns one when **all entries are inactive**.
The dispatcher creates an idle timer only on that result with no current timer.
Otherwise it calls the predicate again: a fresh active result and nonzero timer
cause release followed by a late clear. Idle/nonzero leaves the timer running.
Both timer transitions use fresh log-mode reads and the stock create/delete
messages. Successful transitions return 1; early unchanged/invalid/unready
paths return 0.

The C timer creator `r1_stream_timer_create_back` is the three-argument native
`0x8a368` interface: callback `0x6aca5`, period 1000, context 0. Decompiler extra
arguments are not part of that interface. Stream registration has five actual
arguments; unregister receives the fresh handle as its second argument.

The replay executes the dispatcher and all five native predicates. It covers
all target indices including invalid words, non-boolean enables, individual and
combined sensor masks, shared-user tables, live callback/provider mutations,
registration/timer return values and logging modes. Providers are modeled and
caller-clobbered registers are poisoned. Return, exact call/state sequence,
state guards, preserved registers, SP, masks and FPSCR are checked with a warmed
FPU. This is not physical sensor proof, concurrent execution, a C replacement,
final source-only linking or byte identity.

Correction from consumer instruction review: `0x6c53c` loads once-status from
`0x20006da0`; `0x6ab88` reads the separate cached-ID validity byte at +4.

# R1 BC receive thread creation in C

The stock creator at `0x45054` (36 code bytes) now has one C candidate,
`r1_thread_create_d`, in `runtime/native_bae8_thread.c`.
[Machine receipt](bae8-thread-c-review.json).

The creator calls ThreadNew with the C RX worker, a null argument and the
reconstructed 36-byte CMSIS attribute record. It writes the returned handle to
the existing RX thread owner before testing that returned value for failure.
A provider's changes to the shared handle during ThreadNew are overwritten,
including when ThreadNew returns null. Both stock and C retain an eight-byte
frame at ThreadNew and the failure boundary. The failure calls the already
explicit `r1_bae8_rx_allocation_fault`; its BASEPRI/store transition remains
unimplemented and is not treated as portable C.

Attributes reproduce stock data at `0x99240` under the controlled link:
name `ble_msgrx`, zero attribute bits, 112-byte control-block reservation at
`0x200140b0`, 5,120-byte stack at `0x2000b6f0`, priority 51, TrustZone module
value 1 and reserved value zero. Both RAM reservations have eight-byte
alignment. These sizes establish reservations, not the complete kernel TCB
layout or actual scheduler acceptance.

The eight-byte lifecycle prefix at `0x20006590` has C create/stop pointers,
using the existing receive stop hook. The adjacent thread and queue retain
their existing owners. Executing stock RW initialization over poisoned RAM
proves the native prefix is `{0x45055, 0x4503d}` and both handles start at zero.
A separate poisoned ZI replay proves the stack and control-block reservations
start at zero. Guards surrounding both initialization regions survive. C
callback pointers target the corresponding symbols; their production numeric
addresses are not asserted equal to native addresses.

The worker definition now accepts the CMSIS `void *` argument explicitly and
ignores it. This avoids an incompatible function-pointer cast when ThreadNew
receives its entry. All 601 preceding object files, including the worker,
remain byte-identical to the previous build despite that signature correction.

Verification passed 1,242 paired creator cases, covering null and full-width
returned handles, initial shared handles, interrupt masks, BASEPRI values,
provider mutation, attribute bytes and the failure boundary. The fixture links
the actual C worker and checks that ThreadNew receives its symbol. Five mutants
were rejected: wrong stack size, priority, argument, missing handle publication
and reversed failure condition. The current worker also passed its separate
720-case replay again. Neither test runs an actual scheduler or claims the
modeled ThreadNew created a running thread.

All 602 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. The import sets are unchanged: 161
application imports and 34 bootloader imports. No executable bytes qualify for
the canonical source plan. The fresh hybrid matches the locked application
using unchanged coverage of 4,271 source-built bytes, 641,889 executable
pull-through bytes and 248 resource bytes. This is not source-only completion
or candidate code byte identity. Actual RTOS scheduling, the architectural
failure transition and physical BLE validation remain open.

The subsequent [Cortex-M fault adapter](cortex-fault-c-review.md) supplies the
previously unresolved C provider. Fault-register identity and physical exception
behavior remain unproven.

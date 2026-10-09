# Image-loaded constructor and finalizer binding

The initializer mapping is now image-bound, not a pointer-search hypothesis.
Locked touch SHA256 remains
`0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`.

## Actual reset load

Vector slot1 contains4675, the Thumb entry4674. The tested suffix starts at467E
after the separate hardware/system-init calls. It copies192vector bytes from3300
to20000400, writes that address into the VTOR register backing, then executes
the stock word-copy and zero loops. PC-relative literals46E8..46F4 bind:

| Table | Record | Meaning |
|---|---|---|
| B578..B584 | B58C,200004C0,241 | Copy964bytes toRAM[200004C0,20000884) |
| B584..B58C | 200008A8,428 | Zero1712bytes RAM[200008A8,20000F58) |

Thus flashB948 maps toRAM2000087C and loads3435, the Thumb entry frame_dummy3434.
FlashB94C maps toRAM20000880 and loads3409, the Thumb entry dtors_aux3408.
The constructor's preinit bounds coincide at2000087C; its init array contains
one entry and ends20000880. The finalizer slot follows. This proves the selected
image's static copy/load contract and its offline execution, not that hardware
completed the earlier initialization or selected this image.

## Authentic CRT provider attribution

Pinned official GCC source revision
`a05ea1e5ee0867191bb432a84c055be99dbdbc16` supplies crtstuff.c and build rules.
Authenticated installed thumb/v6-m/nofp/crtbegin.o has relocation-backed init
and fini entries for frame_dummy and __do_global_dtors_aux. Real GNU ld with
bindings read from stock produces exact152instruction/literal bytes:

| Function | Stock extent | Bytes |
|---|---|---|
| deregister_tm_clones | 33C0..33E0 |32|
| register_tm_clones |33E0..3408|40|
| __do_global_dtors_aux |3408..3434|44|
| frame_dummy |3434..3458|36|

Both4byte array entries match their mapped stock initializer bytes. Literal
bindings include empty TM list/end20000884, completed flag200008A8, frame object
200008AC and EH-frame anchorB56C. ITM/frame-registration providers are undefined
weak and resolve zero. No relocation byte was patched. provider-results.json
pins the installed object, linker script, commands, linked ELF and all compared
sections. DSO/unused rodata are explicitly outside this attribution.

This is **binary-provider attribution with authentic source interpretation**,
not source rebuilding of crtstuff.c. Its internal tconfig.h/tsystem.h and full
target/generated build configuration are not available in this selected
acquisition. The authentic source build rules use CRT_BEGIN and CRTSTUFF flags;
no replacement headers/configuration were invented. Reproducing those generated
inputs through an authenticated GCC build is the remaining source-build task,
not a physical-device blocker.

## Behavior now explained without a callback stub

32stock/provider-linked instruction pairs PASS over four initial RAM patterns,
four register seeds and whether the finalizer is explicitly invoked. Stock
copy/zero loops run, load both real callbacks and clear the completed and stdio
handler slots. Constructor executes actual _init, frame_dummy and
register_tm_clones. The registration helpers return because TM list bounds
coincide; the frame registration weak pointer is zero. No external callback
stub is used in these tests.

Manual finalizer invocation first executes deregister_tm_clones and sets its
completed byte1; a second invocation returns without deregistering again.
This is an explicitly invoked interface test, not a natural exit path. The
actual exit path, with zero-loaded stdio-handler and absent exitprocs provider,
reaches the halt loop and does not execute the finalizer. Tests compare RAM
hashes, register/SP preservation, trace order and copy/zero writes.

The stdio-handler begins zero if the recovered loader/reset zero paths execute;
later application writes or installed handlers remain separate questions.
Reset C body's weak atexit reference is also zero at34D0, so that recovered
registration branch is skipped. The presence of a fini-array word and a _fini
section is not evidence of automatic destructor execution.

## Accounting and limits

The prior100source-produced startup bytes passed independent review; focused
runtime source subtotal is922bytes. These new152provider bytes plus8array data
bytes are separately unreviewed binary/data attribution. They add zero claimed
source-produced bytes. PDLcensus remains54/54and4952bytes; whole-firmware gates
remain separate.

Missing earlier board initialization, actual NVIC behavior, application return,
later handler writes, complete reset/live runtime state and producing GCC build
configuration are not inferred. No Git, production, device, canonical ledger or
shared campaign mutation. Source notices/pins and earlier failed comparisons
remain intact. Queue/model discovery was not rerun.

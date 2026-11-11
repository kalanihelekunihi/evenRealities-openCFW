# R1 Cortex-M failure operations through C intrinsics

Two existing handwritten `msr basepri` statements, in the heap failure hook and
shared task lifecycle helper, now use the C compiler intrinsic
`__builtin_arm_wsr("basepri", 64)`. Their complete object files are byte-identical
to the preceding build. The configured Clang compiler is verified here; this
intrinsic is architecture-specific, not portable ISO C or proof of support in
another compiler. [Machine receipt](cortex-fault-c-review.json).

A new shared C provider, `r1_bae8_rx_allocation_fault`, implements the operations
in the RX thread and worker failure blocks at `0x45068` and `0x921f0`: request
BASEPRI 64, attempt a zero word store to `0xffffffff`, then loop forever if the
store returns. It contains no handwritten assembly or executable opcode array.
It resolves the previously explicit RX allocation-fault import. There is no
independent stock function at these inline block addresses; no fictitious
function-frontier entry or canonical source selection was added.

This candidate retains a significant identity boundary. Stock uses 14 bytes;
the C helper uses 18 under the tested link. At the store, stock R0 is zero and
R1 retains its incoming value; C R0 holds `0xffffffff` and R1 is zero. Calls to
the shared helper also change LR relative to the stock inline path. These
registers can appear in an exception frame, so matching the attempted write
and mask effects does not establish exception-frame equivalence. No code-byte,
fault-register or physical exception identity is claimed.

Verification compares both native inline blocks and the C helper across 192
three-way cases. Cases vary initial BASEPRI, PRIMASK, CONTROL including both
stack selections, and stack offsets. The actual attempted store address, size
and value, accessible mask/control register views, and SP are compared.
Privileged execution requests BASEPRI 64; unprivileged execution leaves its
accessible BASEPRI view unchanged in this emulator. Initial state is set before
entering unprivileged mode, whose register views can hide mask values. This
checks the emulator's observed behavior rather than proving physical privilege
or interrupt behavior.

Unmapped stores raise an emulator memory error. A separate controlled mode skips
only the faulting instruction to verify the subsequent permanent loop; it does
not claim the actual store succeeded. Five mutants were rejected: wrong BASEPRI
value, wrong address, wrong store value, wrong CPU register and wrong loop.
Another 32 paired cases link and execute the actual C creator, worker and failure
provider through the attempted store. ThreadNew, queue creation and sync remain
modeled. The native/C caller frames agree at eight bytes for creation failure
and zero for worker failure; raw fault-entry scratch registers and LR remain
outside that comparison and are explicitly retained as gaps.

All 603 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. All preceding 602 objects remain
identical. Application imports decrease to 160; bootloader imports remain 34.
The canonical source plan is unchanged. The fresh hybrid reproduces the locked
application with 4,271 source-built bytes, 641,889 executable pull-through bytes
and 248 resource bytes. The helper is a C source provider, not a byte-qualified
replacement or evidence of a complete source-only firmware build.

Physical exception entry, exception stacking, handler behavior and hardware
execution remain unverified. The receive creation and worker reviews' earlier
unresolved-provider statements describe their historical step; this provider
now supplies their C linkage while retaining the identity boundaries above.

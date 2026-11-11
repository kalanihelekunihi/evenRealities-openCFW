# R1 HR mode transition and setter in C

The transition at 0x49838 and setter at 0x499c4 now use C. The setter rejects requested modes at or above four, runs transition effects using the current mode, and only then writes the requested mode byte. Equal modes log and return from the transition without teardown; the setter still performs its final byte store.

A changed mode unregisters and clears the old mode's HR handle when nonzero. Leaving mode one releases the interval timer, invokes the existing HR timer release, and tears down the HRV session/timer when needed. Both session flags are then cleared. Entering mode one creates a 600,000-unit front timer only when its field is zero. It logs the 600-second request even when creation returns zero.

Stock's initial mode is four, so transition reads a fifth handle slot beyond the previous four-word C owner. The canonical HR array now owns 20 bytes at 0x2001a2ec, ending exactly at the HRV session buffer at 0x2001a300. Stock RW/ZI startup execution on poisoned SRAM, guarded regions and an independent RW decoder confirm all 20 bytes are zero. Existing stop loops still process four slots, matching stock. Wrapped raw index addressing is preserved without adding a bounds policy.

Stock/C tests pass 2,340 direct/setter/mixed-stop cases over initial and invalid modes, equal modes, handles, timers, allocation failure, wrapped mapped slot addresses and provider mutation. Existing controller and result regressions pass another 1,512 and 2,790 cases. Eight compiled defects are rejected. Checks include call order/arguments and state snapshots, full guarded state/buffer contents, callback identity, preserved registers, SP and masks.

All 754 R1 units compile with no failures or duplicate strong symbols. Of 753 prior objects, 752 are identical; the changed owner's existing allocated code and relocations are identical and only four zero state bytes are added. The mode-event import closes while the timing callback becomes explicit, leaving 135 application and 34 bootloader imports. The R1 source check passes; the global check currently flags the concurrent G2 resident_rom_thumb_set.S manifest gap.

The new tests execute the existing C release/teardown helpers. Stream/timer/authorization/logging/clear services are modeled. The timing callback is checked by identity but not invoked. Asynchronous scheduling, physical streams, out-of-map fault recovery, final RAM placement and complete firmware linkage remain unproved. See [machine-readable evidence](hr-mode-transition-c-review.json) and [REA teardown-order receipt](hr-mode-transition-c-rea.json).

The subsequent [HR timing review](hr-timing-c-review.md) now closes the timing callback import and supplies its result/timeout bodies with shared-state and NV-gate replay.

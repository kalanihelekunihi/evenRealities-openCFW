# R1 SpO2 once and mode controls in C

The once control at 0x4aaf8, mode transition at 0x4ab40 and setter at 0x4ad7c now use C. Existing event-service names alias the once control and setter. The original event adapters execute unchanged in the tests.

Once control registers the SpO2/once result callback with both registration arguments one when enabled and no handle exists. Disabling unregisters and clears only the once slot. Direct calls treat any nonzero value as enabled and ignore length; the adapter's existing length/normalization behavior remains intact.

The setter accepts only requested modes zero and one, executes transition effects, then stores the requested mode. Equal modes only log in the transition. A changed mode unregisters and clears the previous slot. Leaving mode one invokes the existing timer release and then clears both timing flags. No new timer is created by the mode transition.

Stock initial mode is two, and its transition indexes a third handle slot. The canonical array now owns 12 bytes at 0x2001a3d0 rather than eight. Together with the unchanged eight-byte timing state, stock RW/ZI startup execution on poisoned SRAM with region guards and an independent RW decoder authenticates 20 initialized bytes. The initial mode remains two and all other bytes are zero. Existing lifecycle loops still process two slots.

Stock/C replay passes 1,254 direct, both actual event-adapter and lifecycle-mixed cases. It covers initial/wrapped mapped indices, equal modes, requested-mode rejection, registration failure, ignored direct lengths and provider mutations. Eight compiled defects are rejected. Checks include callback identity, call order/arguments and state snapshots, guarded state/handle bytes, preserved registers, SP and masks.

All 757 R1 units compile with no failures or duplicate strong symbols. Of 756 prior objects, 755 are identical. The changed owner's existing allocated code and relocations are unchanged; only four zero handle bytes are added. Two event imports close and the once-result callback becomes explicit, leaving 132 application and 34 bootloader imports. The R1 check passes; the global check still flags the existing G2 resident_rom_thumb_set.S manifest gap.

Stream/timer services, logging and companion scheduling are modeled, and the result callback is checked by identity rather than invoked. Existing lifecycle helpers execute as C. No physical streams, asynchronous scheduling, out-of-map recovery, final RAM placement or complete firmware linkage is established. See [machine-readable evidence](spo2-control-c-review.json) and [REA transition receipt](spo2-control-c-rea.json).

The subsequent [SpO2 once-result review](spo2-once-result-c-review.md) closes the result import and replays the actual C callback/controller with shared timing state and calibration support.

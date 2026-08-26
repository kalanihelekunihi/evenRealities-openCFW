# G2 display-driver manager recovery

The twelve retained-path anchors / 2,438 bytes expand to nineteen functions /
2,796 body bytes for `displaydrv_manager.c`. The complete physical object is
`[0x00473952,0x00474550)`, 3,070 bytes. Seven restored routines complete the
manager lifecycle, CMSIS thread/timer control, ULED dispatch, stored completion
callbacks, and display locking/state.

The audit pins 1,035 instructions, 184 direct calls, eighteen whole-image BL
entries, six stored function pointers, one valid interior callback pointer,
and no indirect call or strict-interior ingress. The apparent BL from
`0x00581EA6` into object data at `0x004744AE` is the second halfword of the
valid four-byte `udiv` at `0x00581EA4`, not a missing function.

All 178 external calls terminate at EasyLogger (125), source-owned
CMSIS-FreeRTOS (20), bounded IAR DLIB (11), or first-party ULED/thread/display
providers (22). There are zero direct LVGL or AmbiqSuite calls: those sources
remain behind already identified first-party port/driver seams. The object
therefore reuses EasyLogger `a596b264…`, CMSIS-FreeRTOS `d213f261…`, and
FreeRTOS-Kernel `def7d2df…`, embeds no third-party implementation, and adds no
version or private generating-commit discriminator.

Production closure is now complete. Five authenticated clean-room C files
provide all nineteen functions: `display_thread_init.c`, `display_runtime.c`,
`display_manager_thread.c`, `display_queue_senders.c`, and
`display_lifecycle.c`. Their 4,002 compiled function bytes are installed by
nineteen guarded redirects covering 2,798 stock bytes; 272 bytes of literal,
alignment, and compatibility data remain authenticated stock. The analyzer
now fails closed on every source digest, entry address, target symbol, stock
span, and redirect digest. Its three focused tests and all five host behavior
fixture groups pass.

Live ULED transfer, bilateral display state, timer/concurrency, lock, and
power-transition validation remains blocked by unavailable physical evidence:
the authorized right temple is nonresponsive, the left must remain stock, and
no responsive authorized pair or golden display trace is available. No image
was signed, flashed, or installed during this closure.

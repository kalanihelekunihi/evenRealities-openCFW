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
version or private generating-commit discriminator. It is not
production-routed.

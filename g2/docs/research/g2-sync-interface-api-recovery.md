# G2 sync-interface API recovery

The complete `framework\sync\sync_interface_api.c` object contains thirteen
path-anchored functions / 6,136 executable bytes in physical interval
`[0x004646F0,0x00466010)`, 6,432 bytes. The remaining 296 bytes are bounded
literals, retained strings, and alignment. The audit pins 2,350 instructions,
353 direct calls, 329 whole-image BL entries, one stored Thumb callback, no
indirect calls, and zero strict-interior ingress.

All 333 external direct calls are classified: 255 EasyLogger diagnostics;
seventeen exact CMSIS-FreeRTOS v10.5.1 event/thread/queue wrappers; nine calls
to the bounded FreeRTOS assert port; thirteen IAR DLIB memory operations; 33
calls to the production-routed TLSF-backed heap wrappers; and six calls to the
first-party role-state provider. The object embeds no reusable third-party
implementation.

The dependency evidence therefore reinforces CMSIS-FreeRTOS commit
`d213f261…` and FreeRTOS-Kernel commit `def7d2df…` without adding a version or
historical-commit discriminator. The object is not production-routed;
remaining work is clean-room reconstruction of the first-party message/event
schema and hardware validation.

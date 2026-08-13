# G2 sync-framework recovery

The retained-path census initially exposed 23 functions / 10,954 bytes for
`framework\sync\sync_framework.c`. Whole-image direct-entry, stored-pointer,
and callback-table recovery expands that object to 43 functions and 16,816
reachable executable bytes. The complete physical interval is
`[0x0045A578,0x0045EC7C)`, 18,180 bytes, including 1,364 bytes of literals,
tables, strings, and alignment. The twenty restored functions include the
generic listener trampoline, a missed 1,074-byte TinyFrame listener, two
synchronization entry points, and ten multipart listener handlers.

The fail-closed inventory authenticates 6,083 instructions, 1,070 direct
calls, 79 whole-image BL entries, 24 stored Thumb pointers, fourteen indirect
callback sites, and zero strict-interior ingress. The stored pointers recover
the master/slave TinyFrame listeners and the ten multipart handler pairs. The
indirect calls consume caller-supplied or decoded first-party callbacks; they
do not introduce a hidden third-party implementation body.

Every reusable direct edge is classified. The object calls EasyLogger 825
times, fifteen exact CMSIS-FreeRTOS v10.5.1 wrappers 35 times, FreeRTOS kernel
leaves four times, TinyFrame v1.3.0-lineage entries 26 times, AmbiqSuite GPIO
HAL twice, nanopb once, bounded IAR DLIB primitives seventeen times, and the
production-routed TLSF-backed heap wrappers 86 times. The remaining edges are
eighteen first-party thread-pool calls, one source-owned delay wrapper, and 36
bounded G2 policy/service calls.

This reinforces existing provenance rather than adding a new discriminator:
CMSIS-FreeRTOS `d213f261…`, FreeRTOS-Kernel `def7d2df…`, TinyFrame
`eb75483e…`, AmbiqSuite `5efc0228…`, nanopb `98bf4db6…`, and EasyLogger
`a596b264…`. No third-party definition is embedded in the object, and the
private firmware-producing commit remains unobservable.

The object is not production-routed. Remaining work is clean-room recovery of
the synchronization state machine, event schemas, listener policy, and
hardware/UI validation—not third-party dependency discovery.

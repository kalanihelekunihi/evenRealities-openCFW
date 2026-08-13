# G2 EM9305 DFU service recovery

The six retained-path anchors / 2,784 bytes expand to seven functions / 2,802
body bytes for `platform\service\DFU\service_em9305_dfu.c`. The complete
physical object is `[0x0052F442,0x0052FF4C)`, 2,826 bytes. The fail-closed
audit pins 1,062 instructions, 156 direct calls, seven whole-image BL entries,
no indirect calls, and no strict-interior ingress.

The filename does not imply linked EM9305 vendor code: the object has zero
direct Packetcraft/EM9305 calls. All 152 external calls terminate at
EasyLogger (125), production-owned file/TLSF wrappers (18), bounded IAR DLIB
(4), the shared nanopb-compatible zero initializer (1), or two adjacent
first-party DFU providers (4). The initializer does not add nanopb behavior.

This object therefore adds no EM9305 source/version/commit discriminator. It
reuses EasyLogger `a596b264…`, littlefs/TLSF runtime sources, and the shared
initializer admitted at nanopb compatibility commit `98bf4db6…`. Remaining
work is first-party DFU transport/state reconstruction plus licensed controller
and hardware validation; the object is not production-routed.

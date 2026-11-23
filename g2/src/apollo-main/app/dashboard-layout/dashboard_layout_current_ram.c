/* Native dashboard layout destination at 0x200e7934; 128-byte copy extent. */
#include <stdint.h>

/* Stock .data initialises the live layout with the default (ROM 0x6d52d8):
 * 00 05 00 01 02 04 03 00 01 00 00 00 00 01 04 00, rest zero. Nothing
 * resets it at boot before dashboard readers use it. */
uint8_t audio_dashboard_layout_current[128]
    __attribute__((section(".data.opencfw.dashboard.layout.current"), aligned(4), used)) = {
    0x00u, 0x05u, 0x00u, 0x01u, 0x02u, 0x04u, 0x03u, 0x00u,
    0x01u, 0x00u, 0x00u, 0x00u, 0x00u, 0x01u, 0x04u, 0x00u,
};

_Static_assert(sizeof(audio_dashboard_layout_current) == 128u, "layout copy extent");

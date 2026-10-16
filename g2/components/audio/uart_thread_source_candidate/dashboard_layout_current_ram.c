/* Native dashboard layout destination at 0x200e7934; 128-byte copy extent. */
#include <stdint.h>

uint8_t audio_dashboard_layout_current[128]
    __attribute__((section(".bss.opencfw.dashboard.layout.current"), aligned(4), used));

_Static_assert(sizeof(audio_dashboard_layout_current) == 128u, "layout copy extent");

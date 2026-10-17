/* Selected seven-word font configuration state extents in initialized RAM.
 * Full original allocations and final image startup copy remain open. */
#include <stdint.h>

#define FONT_ACTIVE(name) \
    __attribute__((section(".data.opencfw.font." #name "_active"), aligned(4), used)) \
    uint32_t audio_uart_font_##name##_active[7]

FONT_ACTIVE(primary) = {0x004b26a5u, 0x004b239du, 0u, 0x1au,
                        0x6u, 0x1fd00u, 0u};
FONT_ACTIVE(secondary) = {0x004b26a5u, 0x004b239du, 0u, 0x1cu,
                          0x6u, 0x1fd00u, 0u};

_Static_assert(sizeof(audio_uart_font_primary_active) == 28, "primary selected extent");
_Static_assert(sizeof(audio_uart_font_secondary_active) == 28, "secondary selected extent");

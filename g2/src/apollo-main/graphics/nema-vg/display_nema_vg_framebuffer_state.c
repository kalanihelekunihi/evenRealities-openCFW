/* Apollo MAIN s200 v2.2.6.10 VG framebuffer descriptor at 0x200732e8.
 * Native stores address words 0..14. The next identified RAM object starts
 * at 0x20073324, exactly 15 words later. Initial contents are zeroed by
 * the authenticated startup callback; final placement remains a linker gate. */
#include <stdint.h>

volatile uint32_t audio_uart_nema_vg_framebuffer_descriptor_200732e8[15];

_Static_assert(sizeof(audio_uart_nema_vg_framebuffer_descriptor_200732e8) == 60u,
               "VG framebuffer descriptor extent");

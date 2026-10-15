/* Main graphics-mode call name for the already sourced Nema command encoder.
 * Both names identify the stock routine at 0x513924; the implementation is
 * display_driver_nema_mode_513924 in the Main GPU source closure. */
#include <stdint.h>

extern void display_driver_nema_mode_513924(uint32_t, uint32_t, uint32_t,
                                             uint32_t);

void audio_uart_display_graphics_blend_513924(uint32_t mode, uint32_t target,
                                               uint32_t blend, uint32_t source) {
    display_driver_nema_mode_513924(mode, target, blend, source);
}

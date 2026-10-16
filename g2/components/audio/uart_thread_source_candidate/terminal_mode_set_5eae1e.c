/* Stock Terminal mode-set forwarding wrapper 0x5eae1e. */
#include <stdint.h>

extern void audio_terminal_event_emit_5eadd4(uint32_t mode,
                                               uint32_t mask,
                                               const void *payload);

void audio_terminal_mode_set_5eae1e(uint32_t mode, uint32_t mask) {
    audio_terminal_event_emit_5eadd4((uint8_t)mode, (uint16_t)mask, 0);
}

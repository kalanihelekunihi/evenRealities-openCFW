/* Compatibility for the prior selected terminal object. The source terminal
 * handler calls the native-addressed gateway directly on a clean rebuild. */
#include <stdint.h>

extern void audio_uart_ring_wear_persist_48eb32(uint32_t, uint32_t,
                                                const void *);

void audio_settings_persist_event(uint32_t key, uint32_t length,
                                  const void *payload) {
    audio_uart_ring_wear_persist_48eb32(key, length, payload);
}

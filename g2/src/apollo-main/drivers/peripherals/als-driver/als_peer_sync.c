/* ALS brightness publication, stock driver\sensor\als\als.c.
 * Native 0x4ad9b8..0x4ad9e2 and 0x4adf04..0x4adf34.
 *
 * The driver never drives the display directly: it publishes the new level as
 * the 2-byte sync message 0x10e {brightness_level, notify_app} through the
 * sync interface 0x464d1c. ALSSyncHandler (0x4ae73c, als-sync) consumes it,
 * stores the setting, calls the display callback and, when notify_app is set,
 * reports device status to the phone. */
#include <stdint.h>
#include "g2_als.h"

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern int32_t audio_uart_input_event_send_464d1c(uint16_t, const void *, uint32_t, uint32_t);

void als_function_01(uint8_t level, uint8_t notify_app)
{
    uint8_t message[2];
    audio_uart_buffer_zero(message, sizeof message, 0u);
    message[0] = level;
    message[1] = notify_app;
    (void)audio_uart_input_event_send_464d1c(G2_ALS_SYNC_MESSAGE, message, sizeof message, 0u);
}

/* Record the brightness now being applied and publish it. */
void als_function_23(uint32_t level, uint8_t notify_app)
{
    audio_als_manual_level = level;
    audio_als_manual_level_copy = level;
    audio_als_manual_pending = notify_app != 0u ? 1u : 0u;
    als_function_01((uint8_t)level, notify_app);
}

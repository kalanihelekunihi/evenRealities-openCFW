/* Cordio no-op reset and event handlers, stock Thumb 0x4d29be/0x4d29c0. */
#include <stdint.h>

void audio_ble_dm_empty_reset_4d29be(void)
{
}

void audio_ble_dm_empty_handler_4d29c0(void *message)
{
    (void)message;
}

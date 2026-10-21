/* Native Cordio DM message dispatcher at 0x5369d8. */
#include <stdint.h>

extern void (*const audio_ble_dm_dispatch_table_78a880[8])(void *);

void audio_ble_dm_stack_msg_handler_5369d8(void *message)
{
    uint8_t index = ((const uint8_t *)message)[2u] & 7u;
    audio_ble_dm_dispatch_table_78a880[index](message);
}

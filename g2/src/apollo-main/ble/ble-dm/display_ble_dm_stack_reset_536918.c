/* Cordio DM stack reset dispatch at native Apollo Main 0x536918. */
#include <stdint.h>

extern uint8_t audio_ble_dm_stack_rows_200738dc[];
extern uint8_t audio_ble_dm_handler_state[];
extern void WsfTimerStop(void *);
extern void audio_ble_dm_stack_state_init(void);

void audio_ble_dm_stack_reset_536918(void *message)
{
    (void)message;
    uint8_t *const rows = audio_ble_dm_stack_rows_200738dc;
    if (rows[0x18u] == 3u || rows[0x18u] == 2u) {
        WsfTimerStop(rows);
        uint8_t event[4] = {0u, 0u, 0x25u, 0u};
        void (*callback)(void *) = *(void (**)(void *))(void *)(audio_ble_dm_handler_state + 8u);
        callback(event);
        rows[0x18u] = 0u;
    }
    audio_ble_dm_stack_state_init();
}

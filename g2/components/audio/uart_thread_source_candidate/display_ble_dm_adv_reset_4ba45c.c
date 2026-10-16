/* Cordio legacy dmAdvReset, native Thumb 0x4ba45c.
 * Advertising control offsets refer to native dmAdvCb at 0x20073394. */
#include <stdint.h>

extern uint8_t audio_ble_dm_adv_control[];
extern uint8_t audio_ble_dm_handler_state[];
extern void WsfTimerStop(void *timer);
extern void audio_ble_dm_adv_lower(void);
typedef void (*audio_ble_dm_event_callback)(void *);

void audio_ble_dm_adv_reset_4ba45c(void)
{
    const uint8_t state = audio_ble_dm_adv_control[0x1du];
    if (state == 5u || (state == 1u && audio_ble_dm_adv_control[0x18u] != 1u)) {
        uint8_t stopped[4];
        WsfTimerStop(audio_ble_dm_adv_control);
        stopped[2u] = 0x22u;
        stopped[3u] = 0u;
        (*(audio_ble_dm_event_callback *)(void *)(audio_ble_dm_handler_state + 8u))(stopped);
    }
    audio_ble_dm_adv_lower();
}

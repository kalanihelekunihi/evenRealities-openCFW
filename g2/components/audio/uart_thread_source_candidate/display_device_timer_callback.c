/* Native device manager timer callback 0x4c661c. ROM 0x78d3bc
 * supplies zero high halfword; queue item tail remains ambient stack. */
#include <stdint.h>
extern void audio_ble_device_manager_send(const uint8_t *); /* selected 0x4c659a */
void audio_device_manager_timer_callback_4c661c(void *argument) {
    (void)argument;
    uint8_t message[8];
    message[0]=2u;message[1]=0u;message[2]=0u;message[3]=0u;
    audio_ble_device_manager_send(message);
}

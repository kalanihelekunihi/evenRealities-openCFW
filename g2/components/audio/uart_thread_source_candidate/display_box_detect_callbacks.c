/* Native 0x4ac016/0x4ac020 timer callbacks: ring events 1 and 7. */
#include <stdint.h>
extern void audio_ble_master_emit_ring_event(uint8_t); /* selected 0x4ac16c */
void audio_box_detect_timer_callback_4ac016(void *argument) {
    (void)argument;
    audio_ble_master_emit_ring_event(1u);
}
void audio_box_reconnect_timer_callback_4ac020(void *argument) {
    (void)argument;
    audio_ble_master_emit_ring_event(7u);
}

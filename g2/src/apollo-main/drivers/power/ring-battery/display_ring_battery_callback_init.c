/* Native 0x4ff8d4 wrapper and CB_RING_BAT_Init 0x500380. */
#include <stdint.h>
extern uint8_t audio_ring_battery_callback_manager[]; /* RAM 0x20073f90 */
extern uint32_t audio_callback_mgr_init(void *,const char *); /* selected 0x510108 */
static const char callback_type[]="RING_BAT_INFO"; /* ROM 0x7856f0 */
void audio_ring_battery_callback_init_500380(void) {
    (void)audio_callback_mgr_init(audio_ring_battery_callback_manager,callback_type);
}
void audio_ring_battery_callback_wrapper_4ff8d4(void) {
    audio_ring_battery_callback_init_500380();
}

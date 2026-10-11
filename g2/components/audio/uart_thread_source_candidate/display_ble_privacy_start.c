/* Native BLE product privacy startup 0x47a85c, ordered row-loader path. */
#include <stdint.h>
extern uint8_t audio_ble_privacy_rows[10u*200u]; /* live RAM 0x20067a30 */
extern void audio_ble_privacy_cache_maintenance(const void *,uint8_t); /* 0x475014 */
extern void audio_ble_privacy_load_rows(uint8_t *); /* 0x4795dc */
extern void audio_ble_subsystem_child_479418(void); /* selected AppLoadResList */
extern void audio_ble_privacy_dump_row(uint8_t *,uint8_t); /* 0x4789b0 */
void audio_ble_other_handler_start(void) {
    audio_ble_privacy_cache_maintenance(0,1u);
    audio_ble_privacy_load_rows(audio_ble_privacy_rows);
    audio_ble_subsystem_child_479418();
    for(uint32_t i=0;i<10u;i++)
        audio_ble_privacy_dump_row(audio_ble_privacy_rows+i*200u,(uint8_t)i);
}

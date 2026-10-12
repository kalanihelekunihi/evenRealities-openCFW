/* Native pair-record clear helpers 0x47b488 and 0x47b3cc. */
#include <stdint.h>
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *); /* selected 0x479b74 */
extern uint8_t audio_ble_pair_record_validate(uint8_t *); /* 0x47b730 */
void audio_ble_pair_record_clear_a(uint8_t *record,uint8_t value) {
    record[0xc2u]=value;
}
void audio_ble_pair_record_clear_b(uint8_t *record,uint8_t value) {
    record[0x86u]=value;
    (void)audio_ble_privacy_rewrite_record(record);
    (void)audio_ble_pair_record_validate(record);
}

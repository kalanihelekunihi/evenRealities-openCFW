/* Native FUN_0047b48e: copy discovered descriptors then persist/validate record. */
#include <stdint.h>
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected memcpy 0x439be4 */
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *); /* selected 0x479b74 */
extern uint8_t audio_ble_pair_record_validate(uint8_t *); /* selected 0x47b730 */
/* Stock 0x47B48E (AppDbSetHdlList G2 variant) */
void audio_ble_pair_record_attach(uint8_t *record,uint32_t source) {
    (void)audio_queue_copy_bytes(record+0x98u,(const void *)(uintptr_t)source,0x2au);
    (void)audio_ble_privacy_rewrite_record(record);
    (void)audio_ble_pair_record_validate(record);
}

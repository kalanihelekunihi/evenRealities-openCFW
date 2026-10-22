/* Native DmConnSecLevel 0x4b71b2 and pair-name update 0x47b3ae. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* RAM 0x200712a4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *);
extern uint8_t audio_ble_pair_record_validate(uint8_t *);
void audio_ble_pair_record_update_name_47b3ae(uint8_t *record,const uint8_t *name){
    (void)audio_queue_copy_bytes(record+0x87u,name,16u);
    (void)audio_ble_privacy_rewrite_record(record);
    (void)audio_ble_pair_record_validate(record);
}

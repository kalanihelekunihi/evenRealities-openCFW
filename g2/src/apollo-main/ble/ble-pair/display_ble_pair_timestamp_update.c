/* Native AppDbUpdateRecordTimestamp 0x47c084, including overflow path. */
#include <stdint.h>
extern uint32_t audio_ble_pair_timestamp_counter_20074344; /* live RAM */
extern void audio_ble_pair_timestamp_reset_all(void); /* native 0x47c164 */
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *); /* selected 0x479b74 */
extern uint8_t audio_ble_pair_record_validate(uint8_t *); /* native 0x47b730 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="AppDbUpdateRecordTimestamp";
/* Stock 0x47C084 (FUN_0047c084, AppDbUpdateRecordTimestamp) */
void audio_ble_pair_complete_prepare(uint8_t *record) {
    if(!record)return;
    if(audio_ble_pair_timestamp_counter_20074344==UINT32_MAX) {
        static const char plain[]="AppDbUpdateRecordTimestamp: Timestamp counter overflow detected, resetting all timestamps";
        static const char compact[]="[ble.smpdb]AppDbUpdateRecordTimestamp: Timestamp counter overflow detected, resetting all timestamps";
        if(audio_log_flags()&2u)audio_log_extended(2u,module,path,function,0x813u,plain);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x08000000u,compact,compact);
        audio_ble_pair_timestamp_reset_all();
    }
    uint32_t timestamp=++audio_ble_pair_timestamp_counter_20074344;
    for(uint32_t i=0u;i<4u;i++)record[0xc4u+i]=(uint8_t)(timestamp>>(8u*i));
    static const char plain[]="AppDbUpdateRecordTimestamp: Updated timestamp to %lu";
    static const char compact[]="[ble.smpdb]AppDbUpdateRecordTimestamp: Updated timestamp to %lu";
    if(audio_log_flags()&2u)audio_log_extended(4u,module,path,function,0x818u,plain,timestamp);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,compact,compact,timestamp);
    (void)audio_ble_privacy_rewrite_record(record);
    (void)audio_ble_pair_record_validate(record);
}

/* Native AppDbResetAllTimestamps 0x47c164, called on LRU counter overflow. */
#include <stdint.h>
extern uint32_t audio_ble_pair_timestamp_counter_20074344; /* live RAM */
extern uint8_t audio_ble_privacy_rows[10u*200u]; /* live RAM 0x20067a30 */
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *); /* selected 0x479b74 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="AppDbResetAllTimestamps";
#define LOG(level,line,mask,plain,compact,...) do { \
 if(audio_log_flags()&2u)audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
void audio_ble_pair_timestamp_reset_all(void) {
    LOG(4u,0x82bu,0x10000000u,
        "AppDbResetAllTimestamps: Resetting all record timestamps",
        "[ble.smpdb]AppDbResetAllTimestamps: Resetting all record timestamps");
    audio_ble_pair_timestamp_counter_20074344=0u;
    for(uint32_t index=0u;index<10u;index++) {
        uint8_t *row=audio_ble_privacy_rows+index*200u;
        if(!row[0x2fu]||!row[0x30u])continue;
        uint32_t timestamp=++audio_ble_pair_timestamp_counter_20074344;
        for(uint32_t i=0u;i<4u;i++)row[0xc4u+i]=(uint8_t)(timestamp>>(8u*i));
        LOG(4u,0x835u,0x10800000u,
            "AppDbResetAllTimestamps: Reset record[%d] timestamp to %lu",
            "[ble.smpdb]AppDbResetAllTimestamps: Reset record[%d] timestamp to %lu",
            index,timestamp);
        (void)audio_ble_privacy_rewrite_record(row);
    }
    LOG(4u,0x83eu,0x10000000u,
        "AppDbResetAllTimestamps: All timestamps reset successfully",
        "[ble.smpdb]AppDbResetAllTimestamps: All timestamps reset successfully");
}

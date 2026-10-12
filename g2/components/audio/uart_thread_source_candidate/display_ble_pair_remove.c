/* Native AppDbClearRecordByMacAddr 0x47b59c and its RAM lookup/clear children. */
#include <stdint.h>
extern uint8_t audio_ble_privacy_rows[10u*200u];
extern uint32_t audio_ble_pair_timestamp_counter_20074344;
extern uint8_t DmHostAddrType(uint8_t);
extern uint32_t audio_ble_privacy_compare_address(const uint8_t *,const uint8_t *);
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *);
extern uint8_t audio_ble_pair_record_validate(uint8_t *);
extern void DmPrivRemDevFromResList(uint8_t,const uint8_t *,uint8_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="AppDbClearRecordByMacAddr";
#define LOG(level,line,plain,compact) do { \
 if(audio_log_flags()&2u)audio_log_extended(level,module,path,function,line,plain); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output((level)==1u?0x04000000u:0x10000000u,compact,compact); \
} while(0)
uint8_t *audio_ble_pair_record_by_mac(uint8_t type,const uint8_t *address) {
    uint8_t host_type=DmHostAddrType(type);
    for(uint32_t i=0;i<10u;i++) {
        uint8_t *row=audio_ble_privacy_rows+i*200u;
        if(row[0x2fu]&&row[6u]==host_type&&audio_ble_privacy_compare_address(row,address)) {
            uint32_t timestamp=++audio_ble_pair_timestamp_counter_20074344;
            for(uint32_t j=0;j<4u;j++)row[0xc4u+j]=(uint8_t)(timestamp>>(8u*j));
            return row;
        }
    }
    return 0;
}
__attribute__((noinline)) void audio_ble_pair_record_clear_full(uint8_t *record) {
    record[0x2fu]=0u;record[0x30u]=0u;
    (void)audio_ble_privacy_rewrite_record(record);
    (void)audio_ble_pair_record_validate(record);
}
uint8_t audio_ble_remove_pair(uint8_t type,const uint8_t *address) {
    if(!address) {
        LOG(1u,0x74cu,"AppDbClearRecordByMacAddr: Invalid MAC address pointer",
            "[ble.smpdb]AppDbClearRecordByMacAddr: Invalid MAC address pointer");
        return 0u;
    }
    uint8_t *record=audio_ble_pair_record_by_mac(type,address);
    if(!record) {
        LOG(4u,0x765u,"AppDbClearRecordByMacAddr: No matching record found",
            "[ble.smpdb]AppDbClearRecordByMacAddr: No matching record found");
        return 0u;
    }
    LOG(4u,0x755u,"AppDbClearRecordByMacAddr: Found matching record, clearing completely",
        "[ble.smpdb]AppDbClearRecordByMacAddr: Found matching record, clearing completely");
    audio_ble_pair_record_clear_full(record);
    DmPrivRemDevFromResList(record[6u],record,0u);
    LOG(4u,0x760u,"AppDbClearRecordByMacAddr: Record completely cleared successfully",
        "[ble.smpdb]AppDbClearRecordByMacAddr: Record completely cleared successfully");
    return 1u;
}

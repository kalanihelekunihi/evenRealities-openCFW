/* Native AppDbShowAllRecordsStatus 0x47bc30: MRAM census and diagnostics. */
#include <stdint.h>
extern const uint8_t audio_ble_mram_records_7ff000[10u*256u]; /* mapped product MRAM */
extern uint32_t audio_ble_pair_timestamp_counter_20074344;
extern void audio_ble_privacy_cache_maintenance(const void *,uint8_t); /* selected 0x475014 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="AppDbShowAllRecordsStatus";
#define LOG(level,line,mask,plain,compact,...) do { \
 if(audio_log_flags()&2u)audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
/* Stock 0x47BC30 (FUN_0047bc30, AppDbShowAllRecordsStatus) */
void audio_ble_pair_complete_commit(void) {
    LOG(4u,0x7d3u,0x10000000u,"=== AppDbShowAllRecordsStatus ===",
        "[ble.smpdb]=== AppDbShowAllRecordsStatus ===");
    LOG(4u,0x7d4u,0x10400000u,"Total records: %d",
        "[ble.smpdb]Total records: %d",10u);
    LOG(4u,0x7d5u,0x10400000u,"Global timestamp counter: %lu",
        "[ble.smpdb]Global timestamp counter: %lu",audio_ble_pair_timestamp_counter_20074344);
    uint32_t oldest=UINT32_MAX,newest=0u,count=0u,min_index=0u,max_index=0u;
    audio_ble_privacy_cache_maintenance(0,1u);
    for(uint32_t index=0u;index<10u;index++) {
        const uint8_t *row=audio_ble_mram_records_7ff000+index*256u;
        uint32_t timestamp=word(row+0xc4u);
        if(!row[0x30u]||!row[0x2fu]) {
            if(!row[0x2fu])
                LOG(4u,0x7f7u,0x10800000u,
                    "Record[%d]: Valid=FALSE, InUse=FALSE, Timestamp=%lu",
                    "[ble.smpdb]Record[%d]: Valid=FALSE, InUse=FALSE, Timestamp=%lu",index,timestamp);
            else
                LOG(4u,0x7f4u,0x10800000u,
                    "Record[%d]: Valid=FALSE, InUse=TRUE, Timestamp=%lu",
                    "[ble.smpdb]Record[%d]: Valid=FALSE, InUse=TRUE, Timestamp=%lu",index,timestamp);
            continue;
        }
        count++;
        LOG(4u,0x7e4u,0x10c00000u,
            "Record[%d]: Valid=TRUE, InUse=TRUE, Timestamp=%lu, KeyMask=0x%02x",
            "[ble.smpdb]Record[%d]: Valid=TRUE, InUse=TRUE, Timestamp=%lu, KeyMask=0x%02x",
            index,timestamp,row[0x2eu]);
        LOG(4u,0x7e7u,0x11c00000u,
            "  Device: %02X:%02X:%02X:%02X:%02X:%02X (Type=%d)",
            "[ble.smpdb]  Device: %02X:%02X:%02X:%02X:%02X:%02X (Type=%d)",
            row[5],row[4],row[3],row[2],row[1],row[0],row[6]);
        if(timestamp<oldest) {oldest=timestamp;min_index=index;}
        if(timestamp>newest) {newest=timestamp;max_index=index;}
    }
    LOG(4u,0x7fbu,0x10800000u,"Valid records: %d/%d",
        "[ble.smpdb]Valid records: %d/%d",count,10u);
    if(count) {
        LOG(4u,0x7fdu,0x10800000u,"Oldest record: [%d] with timestamp %lu",
            "[ble.smpdb]Oldest record: [%d] with timestamp %lu",min_index,oldest);
        LOG(4u,0x7feu,0x10800000u,"Newest record: [%d] with timestamp %lu",
            "[ble.smpdb]Newest record: [%d] with timestamp %lu",max_index,newest);
    }
    LOG(4u,0x800u,0x10000000u,"=== End AppDbShowAllRecordsStatus ===",
        "[ble.smpdb]=== End AppDbShowAllRecordsStatus ===");
}

/* Native AppDbShowNvmStatus 0x47c2bc and AppDbClearRecordByConnId 0x47c8cc. */
#include <stdint.h>
extern const uint8_t audio_ble_mram_records_7ff000[10u*256u];
extern void audio_ble_privacy_cache_maintenance(const void *,uint8_t);
extern uint8_t *audio_ble_pair_record(uint8_t);
extern uint8_t audio_ble_remove_pair(uint8_t,const uint8_t *);
extern void audio_ble_pair_storage_refresh(void); /* native 0x4b4720 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
#define LOG(fn,level,line,mask,plain,compact,...) do { \
 if(audio_log_flags()&2u)audio_log_extended(level,module,path,fn,line,plain,##__VA_ARGS__); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
void audio_ble_pair_failure_prepare(void) {
    static const char fn[]="AppDbShowNvmStatus";
    LOG(fn,4u,0x84bu,0x10000000u,"=== AppDbShowNvmStatus ===","[ble.smpdb]=== AppDbShowNvmStatus ===");
    uint32_t valid=0;
    audio_ble_privacy_cache_maintenance(0,1u);
    for(uint32_t i=0;i<10u;i++) {
        const uint8_t *row=audio_ble_mram_records_7ff000+i*256u;
        if(row[0x2fu]&&row[0x30u]&&row[0]&&row[0]!=0xffu) {
            valid++;
            LOG(fn,4u,0x85bu,0x12000000u,
                "Record[%d]: Valid=TRUE, KeyMask=0x%02x, Device=%02X:%02X:%02X:%02X:%02X:%02X",
                "[ble.smpdb]Record[%d]: Valid=TRUE, KeyMask=0x%02x, Device=%02X:%02X:%02X:%02X:%02X:%02X",
                i,row[0x2e],row[5],row[4],row[3],row[2],row[1],row[0]);
        }
    }
    LOG(fn,4u,0x860u,0x10800000u,"NVM Status:%d/%d records valid","[ble.smpdb]NVM Status:%d/%d records valid",valid,10u);
    LOG(fn,4u,0x861u,0x10400000u,"NVM Address: 0x%08x","[ble.smpdb]NVM Address: 0x%08x",(uint32_t)(uintptr_t)audio_ble_mram_records_7ff000);
    LOG(fn,4u,0x862u,0x10800000u,"Record Size: %d bytes (%d words)","[ble.smpdb]Record Size: %d bytes (%d words)",256u,64u);
    LOG(fn,4u,0x863u,0x10000000u,"=== End AppDbShowNvmStatus ===","[ble.smpdb]=== End AppDbShowNvmStatus ===");
}
void audio_ble_pair_failure_clear(uint8_t conn) {
    static const char fn[]="AppDbClearRecordByConnId";
    uint8_t *record=audio_ble_pair_record(conn);
    if(!record) {
        LOG(fn,4u,0x8d0u,0x10400000u,
            "DM_SEC_PAIR_FAIL_IND: No database handle found for connection %d - no action needed",
            "[ble.smpdb]DM_SEC_PAIR_FAIL_IND: No database handle found for connection %d - no action needed",conn);
        return;
    }
    if(!record[0x30u]||(record[0x2eu]&5u)==0u) {
        LOG(fn,4u,0x8c9u,0x10c00000u,
            "DM_SEC_PAIR_FAIL_IND: Connection %d has no valid pairing record to clear (valid=%d, keyMask=0x%02x)",
            "[ble.smpdb]DM_SEC_PAIR_FAIL_IND: Connection %d has no valid pairing record to clear (valid=%d, keyMask=0x%02x)",
            conn,record[0x30u],record[0x2eu]);
        record[0x30u]=0;record[0x2fu]=0;
        return;
    }
    LOG(fn,2u,0x8bbu,0x09800000u,
        "DM_SEC_PAIR_FAIL_IND: Clearing valid pairing record for device %02X:%02X:%02X:%02X:%02X:%02X",
        "[ble.smpdb]DM_SEC_PAIR_FAIL_IND: Clearing valid pairing record for device %02X:%02X:%02X:%02X:%02X:%02X",
        record[5],record[4],record[3],record[2],record[1],record[0]);
    if(!audio_ble_remove_pair(record[6],record))
        LOG(fn,1u,0x8c2u,0x04000000u,
            "DM_SEC_PAIR_FAIL_IND: Failed to clear storage info for the device",
            "[ble.smpdb]DM_SEC_PAIR_FAIL_IND: Failed to clear storage info for the device");
    else
        LOG(fn,4u,0x8c0u,0x10000000u,
            "DM_SEC_PAIR_FAIL_IND: Successfully cleared all storage info for the device",
            "[ble.smpdb]DM_SEC_PAIR_FAIL_IND: Successfully cleared all storage info for the device");
    audio_ble_pair_storage_refresh();
}

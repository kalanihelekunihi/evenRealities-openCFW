/* Native AppDbVerifyMramWrite 0x47b730: selected row comparison and key checks. */
#include <stdint.h>
extern const uint8_t audio_ble_mram_records_7ff000[10u*256u]; /* mapped MRAM, product storage */
extern void audio_ble_privacy_cache_maintenance(const void *,uint8_t); /* selected 0x475014 */
extern uint32_t audio_ble_privacy_compare_address(const uint8_t *,const uint8_t *); /* selected 0x4d294a */
extern int32_t g2_lfs_memcmp(const void *,const void *,uint32_t); /* selected 0x4751c8 */
extern void audio_dump_hex(const char *,uint32_t,const uint8_t *,uint32_t); /* selected 0x43dacc */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="AppDbVerifyMramWrite";
#define LOG(level,line,mask,plain,compact,...) do { \
 if(audio_log_flags()&2u)audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
static uint8_t key_check(const uint8_t *ram,const uint8_t *mram,uint32_t offset,
                         const char *ok_text,const char *ok_short,uint32_t ok_line,
                         const char *bad_text,const char *bad_short,uint32_t bad_line,
                         const char *ram_label,const char *mram_label) {
    if(g2_lfs_memcmp(ram+offset,mram+offset,16u)==0) {
        LOG(4u,ok_line,0x10000000u,ok_text,ok_short);
        return 1u;
    }
    LOG(1u,bad_line,0x04000000u,bad_text,bad_short);
    audio_dump_hex(ram_label,16u,ram+offset,16u);
    audio_dump_hex(mram_label,16u,mram+offset,16u);
    return 0u;
}
uint8_t audio_ble_pair_record_validate(uint8_t *record) {
    uint8_t valid=1u;
    LOG(4u,0x779u,0x10000000u,
        "AppDbVerifyMramWrite: Starting MRAM write verification",
        "[ble.smpdb]AppDbVerifyMramWrite: Starting MRAM write verification");
    audio_ble_privacy_cache_maintenance(0,1u);
    for(uint32_t index=0u;index<10u;index++) {
        const uint8_t *mram=audio_ble_mram_records_7ff000+index*256u;
        if(!audio_ble_privacy_compare_address(record,mram)||record[6u]!=mram[6u])continue;
        LOG(4u,0x782u,0x10400000u,
            "AppDbVerifyMramWrite: Found matching record at index %d",
            "[ble.smpdb]AppDbVerifyMramWrite: Found matching record at index %d",index);
        if(record[0x30u]!=mram[0x30u]) {
            LOG(1u,0x787u,0x04800000u,
                "AppDbVerifyMramWrite: valid field mismatch - RAM=%d, Flash=%d",
                "[ble.smpdb]AppDbVerifyMramWrite: valid field mismatch - RAM=%d, Flash=%d",
                record[0x30u],mram[0x30u]);valid=0u;
        }
        if(record[0x2fu]!=mram[0x2fu]) {
            LOG(1u,0x78du,0x04800000u,
                "AppDbVerifyMramWrite: inUse field mismatch - RAM=%d, Flash=%d",
                "[ble.smpdb]AppDbVerifyMramWrite: inUse field mismatch - RAM=%d, Flash=%d",
                record[0x2fu],mram[0x2fu]);valid=0u;
        }
        if(record[0x2eu]!=mram[0x2eu]) {
            LOG(1u,0x793u,0x04800000u,
                "AppDbVerifyMramWrite: keyValidMask mismatch - RAM=0x%02x, Flash=0x%02x",
                "[ble.smpdb]AppDbVerifyMramWrite: keyValidMask mismatch - RAM=0x%02x, Flash=0x%02x",
                record[0x2eu],mram[0x2eu]);valid=0u;
        }
        if(record[0x2eu]&1u)
            valid&=key_check(record,mram,0x34u,
                "AppDbVerifyMramWrite: LOCAL_LTK verification passed",
                "[ble.smpdb]AppDbVerifyMramWrite: LOCAL_LTK verification passed",0x79fu,
                "AppDbVerifyMramWrite: LOCAL_LTK mismatch",
                "[ble.smpdb]AppDbVerifyMramWrite: LOCAL_LTK mismatch",0x79au,"RAM LTK","Flash LTK");
        if(record[0x2eu]&4u)
            valid&=key_check(record,mram,7u,
                "AppDbVerifyMramWrite: IRK verification passed",
                "[ble.smpdb]AppDbVerifyMramWrite: IRK verification passed",0x7abu,
                "AppDbVerifyMramWrite: IRK mismatch",
                "[ble.smpdb]AppDbVerifyMramWrite: IRK mismatch",0x7a6u,"RAM IRK","Flash IRK");
        if(record[0x2eu]&8u)
            valid&=key_check(record,mram,0x1eu,
                "AppDbVerifyMramWrite: CSRK verification passed",
                "[ble.smpdb]AppDbVerifyMramWrite: CSRK verification passed",0x7b7u,
                "AppDbVerifyMramWrite: CSRK mismatch",
                "[ble.smpdb]AppDbVerifyMramWrite: CSRK mismatch",0x7b2u,"RAM CSRK","Flash CSRK");
        break;
    }
    if(valid)
        LOG(4u,0x7c2u,0x10000000u,
            "AppDbVerifyMramWrite: All verifications passed",
            "[ble.smpdb]AppDbVerifyMramWrite: All verifications passed");
    else
        LOG(1u,0x7c4u,0x04000000u,
            "AppDbVerifyMramWrite: Verification failed - this may cause DH key check failures",
            "[ble.smpdb]AppDbVerifyMramWrite: Verification failed - this may cause DH key check failures");
    return valid;
}

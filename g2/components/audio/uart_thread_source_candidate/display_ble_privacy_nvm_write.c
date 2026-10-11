/* Native _updateOneRecordToNVM 0x4799a8, two 0x80-byte flash halves. */
#include <stdint.h>
extern uint8_t audio_ble_privacy_nvm_records[10u*256u]; /* NVM 0x7ff000 */
extern void audio_ble_privacy_cache_maintenance(const uint32_t *,uint8_t);
extern uint32_t audio_ble_nvm_write_words(uint32_t,const uint8_t *,uint8_t *,uint32_t); /* 0x4d0a2c */
extern uint32_t audio_ble_nvm_write_aligned(uint32_t,const uint8_t *,uint8_t *,uint32_t); /* 0x4d09d8 */
extern uint32_t g2_log_exception_number(void);
extern int32_t audio_ble_thread_yield(void); /* native osThreadYield */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="_updateOneRecordToNVM";
static const char fail[]="_updateOneRecordToNVM: Flash program failed: rc1=0x%x rc2=0x%x";
static const char fail_short[]="[ble.smpdb]_updateOneRecordToNVM: Flash program failed: rc1=0x%x rc2=0x%x";
static const char success[]="_updateOneRecordToNVM: Flash program success, wrote %d words (2x%lu) at index %d";
static const char success_short[]="[ble.smpdb]_updateOneRecordToNVM: Flash program success, wrote %d words (2x%lu) at index %d";
static int ext(void) { return (audio_log_level()&2u)!=0u; }
static int compact(void) {
    uint32_t p=audio_log_level();
    return (p&1u)!=0u || (audio_log_level()&4u)!=0u;
}
void audio_ble_privacy_nvm_write_record(const uint8_t *record,uint8_t index) {
    uint8_t *slot=audio_ble_privacy_nvm_records+(uint32_t)index*256u;
    audio_ble_privacy_cache_maintenance(0,1u);
    uint32_t first=audio_ble_nvm_write_words(0x12344321u,record,slot,0x20u);
    if(g2_log_exception_number()==0u)
        (void)audio_ble_thread_yield();
    uint32_t second=audio_ble_nvm_write_words(0x12344321u,record+0x80u,slot+0x80u,0x20u);
    if(first==0u && second==0u) {
        if(ext()) audio_log_extended(4u,module,source,function,0x1b3u,success,0x40u,0x20u,index);
        if(compact()) (void)compressed_log_output(0x10c00000u,success_short,success_short,0x40u,0x20u,index);
    } else {
        if(ext()) audio_log_extended(1u,module,source,function,0x1b0u,fail,first,second);
        if(compact()) (void)compressed_log_output(0x04800000u,fail_short,fail_short,first,second);
    }
}
uint32_t audio_ble_nvm_write_words(uint32_t key,const uint8_t *source_bytes,
                                   uint8_t *destination,uint32_t words) {
    if((((uintptr_t)destination&15u)==0u) && ((words&3u)==0u))
        return audio_ble_nvm_write_aligned(key,source_bytes,destination,words);
    return 0x08000140u;
}

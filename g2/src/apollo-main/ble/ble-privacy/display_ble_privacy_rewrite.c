/* Native _AppDbUpdateNVM 0x479b74: ten-row update and role-aware LRU. */
#include <stdint.h>
extern uint8_t audio_ble_privacy_nvm_records[10u*256u];
extern void audio_ble_privacy_cache_maintenance(const void *,uint8_t);
extern uint32_t audio_ble_privacy_compare_address(const uint8_t *,const uint8_t *);
extern void audio_ble_privacy_nvm_write_record(const uint8_t *,uint8_t);
extern void audio_ble_privacy_dump_row(uint8_t *,uint8_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.smpdb";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="_AppDbUpdateNVM";
#define E0(level,line,msg) do { if(audio_log_level()&2u) audio_log_extended(level,module,source,function,line,msg); } while(0)
#define E(level,line,msg,...) do { if(audio_log_level()&2u) audio_log_extended(level,module,source,function,line,msg,__VA_ARGS__); } while(0)
#define C0(flags,msg) do { if((audio_log_level()&1u)||(audio_log_level()&4u)) (void)compressed_log_output(flags,msg,msg); } while(0)
#define C(flags,msg,...) do { if((audio_log_level()&1u)||(audio_log_level()&4u)) (void)compressed_log_output(flags,msg,msg,__VA_ARGS__); } while(0)
static uint32_t timestamp(const uint8_t *row) { return *(const uint32_t *)(const void *)(row+0xc4u); }
static int empty_address(const uint8_t *row) {
    uint8_t zero=1u,erased=1u;
    for(uint32_t j=0;j<6u;j++) { if(row[j]!=0u) zero=0u; if(row[j]!=0xffu) erased=0u; }
    return zero||erased;
}
static void write_and_dump(const uint8_t *new_row,uint8_t index) {
    audio_ble_privacy_nvm_write_record(new_row,index);
    audio_ble_privacy_dump_row((uint8_t *)new_row,index);
}
uint32_t audio_ble_privacy_rewrite_record(uint8_t *record) {
    uint8_t *const rows=audio_ble_privacy_nvm_records;
    E0(4u,0x1beu,"------------------------_AppDbUpdateNVM--------------------");
    C0(0x10000000u,"[ble.smpdb]------------------------_AppDbUpdateNVM--------------------");
    audio_ble_privacy_cache_maintenance(0,1u);
    E(4u,0x1ceu,"_AppDbUpdateNVM: Flash address: 0x%08x, Data size: %d bytes (%d words)",0x7ff000u,0x100u,0x40u);
    C(0x10c00000u,"[ble.smpdb]_AppDbUpdateNVM: Flash address: 0x%08x, Data size: %d bytes (%d words)",0x7ff000u,0x100u,0x40u);
    for(uint32_t i=0;i<10u;i++) {
        uint8_t *row=rows+i*256u;
        if(!empty_address(row) && audio_ble_privacy_compare_address(record,row)) {
            E(4u,0x1e8u,"_AppDbUpdateNVM: Found existing record at index %d, updating",i);
            C(0x10400000u,"[ble.smpdb]_AppDbUpdateNVM: Found existing record at index %d, updating",i);
            write_and_dump(record,(uint8_t)i);
            E(4u,0x1edu,"1 _AppDbUpdateNVM i = %d",i);
            C(0x10400000u,"[ble.smpdb]1 _AppDbUpdateNVM i = %d",i);
            return 1u;
        }
    }
    for(uint32_t i=0;i<10u;i++) {
        uint8_t *row=rows+i*256u;
        if(empty_address(row)) {
            E(4u,0x20eu,"_AppDbUpdateNVM: Found empty slot at index %d, writing new record",i);
            C(0x10400000u,"[ble.smpdb]_AppDbUpdateNVM: Found empty slot at index %d, writing new record",i);
            write_and_dump(record,(uint8_t)i);
            E(4u,0x213u,"2 _AppDbUpdateNVM i = %d ",i);
            C(0x10400000u,"[ble.smpdb]2 _AppDbUpdateNVM i = %d ",i);
            return 1u;
        }
    }
    const char *role=record[0xc3u]?"Master":"Slave";
    E(2u,0x222u,"_AppDbUpdateNVM: NVM is full, using role-specific LRU strategy for %s role",role);
    C(0x08400000u,"[ble.smpdb]_AppDbUpdateNVM: NVM is full, using role-specific LRU strategy for %s role",role);
    uint8_t *victim=0;
    uint32_t index=0u,oldest=UINT32_MAX;
    for(uint32_t i=0;i<10u;i++) {
        uint8_t *row=rows+i*256u;
        audio_ble_privacy_dump_row(row,(uint8_t)i);
        if(row[0x30u]==0u && row[0x2fu]==0u) {
            E(4u,0x231u,"_AppDbUpdateNVM: Found invalid and unused record at index %d",i);
            C(0x10400000u,"[ble.smpdb]_AppDbUpdateNVM: Found invalid and unused record at index %d",i);
            victim=row;index=i;break;
        }
    }
    if(!victim) for(uint32_t i=0;i<10u;i++) {
        uint8_t *row=rows+i*256u;
        if(row[0x30u]==0u && row[0x2fu]==1u && timestamp(row)<oldest) {
            oldest=timestamp(row);victim=row;index=i;
        }
    }
    if(victim && victim[0x2fu]==1u && victim[0x30u]==0u) {
        E(4u,0x249u,"_AppDbUpdateNVM: Found oldest invalid but in-use record at index %d with timestamp %lu",index,oldest);
        C(0x10800000u,"[ble.smpdb]_AppDbUpdateNVM: Found oldest invalid but in-use record at index %d with timestamp %lu",index,oldest);
    }
    if(!victim) {
        for(uint32_t pass=0;pass<3u && !victim;pass++) {
            for(uint32_t i=0;i<10u;i++) {
                uint8_t *row=rows+i*256u;
                uint8_t eligible=(row[0x30u]!=0u && row[0x2fu]!=0u);
                if(pass==0u) eligible=(uint8_t)(eligible && row[0xc3u]==record[0xc3u]);
                if(pass==2u) eligible=(row[0x30u]==0u && row[0x2fu]==1u);
                if(eligible && timestamp(row)<oldest) {
                    oldest=timestamp(row);victim=row;index=i;
                }
            }
        }
    }
    if(!victim) {
        E0(1u,0x29cu,"_AppDbUpdateNVM: No suitable records found for replacement");
        C0(0x04000000u,"[ble.smpdb]_AppDbUpdateNVM: No suitable records found for replacement");
        return 0u;
    }
    E(4u,0x27cu,"_AppDbUpdateNVM: Replacing record[%d] with timestamp %lu",index,timestamp(victim));
    C(0x10800000u,"[ble.smpdb]_AppDbUpdateNVM: Replacing record[%d] with timestamp %lu",index,timestamp(victim));
    E(4u,0x27fu,"_AppDbUpdateNVM: Old device: %02X:%02X:%02X:%02X:%02X:%02X",victim[5],victim[4],victim[3],victim[2],victim[1],victim[0]);
    C(0x11800000u,"[ble.smpdb]_AppDbUpdateNVM: Old device: %02X:%02X:%02X:%02X:%02X:%02X",victim[5],victim[4],victim[3],victim[2],victim[1],victim[0]);
    E(4u,0x282u,"_AppDbUpdateNVM: Debug - oldestIndex=%d",index);
    C(0x10400000u,"[ble.smpdb]_AppDbUpdateNVM: Debug - oldestIndex=%d",index);
    E(4u,0x284u,"_AppDbUpdateNVM: Debug - RAM buffer offset: %d words (%d bytes)",index<<6,index<<8);
    C(0x10800000u,"[ble.smpdb]_AppDbUpdateNVM: Debug - RAM buffer offset: %d words (%d bytes)",index<<6,index<<8);
    E(4u,0x285u,"_AppDbUpdateNVM: Debug - Flash address offset: %d words",index<<6);
    C(0x10400000u,"[ble.smpdb]_AppDbUpdateNVM: Debug - Flash address offset: %d words",index<<6);
    audio_ble_privacy_nvm_write_record(record,(uint8_t)index);
    audio_ble_privacy_cache_maintenance(0,1u);
    victim=rows+index*256u;
    if(audio_ble_privacy_compare_address(victim,record)==0u) {
        E(1u,0x291u,"_AppDbUpdateNVM: LRU replacement failed - verification mismatch at index %d",index);
        C(0x04400000u,"[ble.smpdb]_AppDbUpdateNVM: LRU replacement failed - verification mismatch at index %d",index);
        E(1u,0x294u,"_AppDbUpdateNVM: Expected device: %02X:%02X:%02X:%02X:%02X:%02X",record[5],record[4],record[3],record[2],record[1],record[0]);
        C(0x05800000u,"[ble.smpdb]_AppDbUpdateNVM: Expected device: %02X:%02X:%02X:%02X:%02X:%02X",record[5],record[4],record[3],record[2],record[1],record[0]);
        E(1u,0x297u,"_AppDbUpdateNVM: Found device: %02X:%02X:%02X:%02X:%02X:%02X",victim[5],victim[4],victim[3],victim[2],victim[1],victim[0]);
        C(0x05800000u,"[ble.smpdb]_AppDbUpdateNVM: Found device: %02X:%02X:%02X:%02X:%02X:%02X",victim[5],victim[4],victim[3],victim[2],victim[1],victim[0]);
    } else {
        E(4u,0x28fu,"_AppDbUpdateNVM: LRU replacement successful for device %02X:%02X:%02X:%02X:%02X:%02X at index %d",victim[5],victim[4],victim[3],victim[2],victim[1],victim[0],index);
        C(0x11c00000u,"[ble.smpdb]_AppDbUpdateNVM: LRU replacement successful for device %02X:%02X:%02X:%02X:%02X:%02X at index %d",victim[5],victim[4],victim[3],victim[2],victim[1],victim[0],index);
    }
    return 1u;
}

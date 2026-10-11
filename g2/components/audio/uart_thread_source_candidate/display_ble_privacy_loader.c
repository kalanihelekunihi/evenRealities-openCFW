/* Native _CopyRecListFromNvmToRam 0x4795dc; 10 flash records, 256B stride. */
#include <stdint.h>
extern const uint8_t audio_ble_privacy_nvm_records[10u*256u]; /* NVM 0x7ff000 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_ble_privacy_cache_maintenance(const void *,uint8_t); /* 0x475014 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* 0x439be4 */
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *); /* 0x479b74 */
extern void audio_dump_hex(const char *,uint32_t,const uint8_t *,uint32_t);
static const uint8_t zero_irk[16]={0}; /* ROM 0x784fa0 */
static const char module[]="ble.smpdb";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="_CopyRecListFromNvmToRam";
static const char start[]="_CopyRecListFromNvmToRam: Starting to load records from Flash";
static const char start_short[]="[ble.smpdb]_CopyRecListFromNvmToRam: Starting to load records from Flash";
static const char empty[]="_CopyRecListFromNvmToRam: Found empty record[%d], stopping load";
static const char empty_short[]="[ble.smpdb]_CopyRecListFromNvmToRam: Found empty record[%d], stopping load";
static const char skip[]="_CopyRecListFromNvmToRam: Skipping invalid record[%d] - valid=%d, keyMask=0x%02x";
static const char skip_short[]="[ble.smpdb]_CopyRecListFromNvmToRam: Skipping invalid record[%d] - valid=%d, keyMask=0x%02x";
static const char mismatch[]="_CopyRecListFromNvmToRam: Fixing keyValidMask mismatch for record - stored=0x%02x, actual=0x%02x";
static const char mismatch_short[]="[ble.smpdb]_CopyRecListFromNvmToRam: Fixing keyValidMask mismatch for record - stored=0x%02x, actual=0x%02x";
static const char irk[]="_CopyRecListFromNvmToRam: Record[%d] has IRK - KeyMask=0x%02x";
static const char irk_short[]="[ble.smpdb]_CopyRecListFromNvmToRam: Record[%d] has IRK - KeyMask=0x%02x";
static const char loaded[]="_CopyRecListFromNvmToRam: Loaded record[%d] with keys=0x%02x, valid=%d, addr=%02X:%02X:%02X:%02X:%02X:%02X";
static const char loaded_short[]="[ble.smpdb]_CopyRecListFromNvmToRam: Loaded record[%d] with keys=0x%02x, valid=%d, addr=%02X:%02X:%02X:%02X:%02X:%02X";
static const char summary[]="_CopyRecListFromNvmToRam: Loaded %d valid records from Flash";
static const char summary_short[]="[ble.smpdb]_CopyRecListFromNvmToRam: Loaded %d valid records from Flash";
static const char peer_irk[]="Peer IRK";
static int has_bytes(const uint8_t *p) {
    for(uint32_t i=0;i<16u;i++) if(p[i]!=zero_irk[i]) return 1;
    return 0;
}
static void clear_row(uint8_t *p) { for(uint32_t i=0;i<200u;i++) p[i]=0u; }
static int extended(void) { return (audio_log_level()&2u)!=0u; }
static int compact(void) {
    uint32_t p=audio_log_level();
    return (p&1u)!=0u || (audio_log_level()&4u)!=0u;
}
void audio_ble_privacy_load_rows(uint8_t *destination) {
    uint8_t record[200];
    uint8_t valid_count=0u;
    if(extended()) audio_log_extended(4u,module,source,function,0x13au,start);
    if(compact()) (void)compressed_log_output(0x10000000u,start_short,start_short);
    audio_ble_privacy_cache_maintenance(0,1u);
    for(uint8_t index=0;index<10u;index++) {
        const uint8_t *flash=audio_ble_privacy_nvm_records+(uint32_t)index*256u;
        (void)audio_queue_copy_bytes(record,flash,200u);
        uint32_t id=*(const uint32_t *)(const void *)record;
        if(id==0u || id==UINT32_MAX) {
            if(extended()) audio_log_extended(4u,module,source,function,0x188u,empty,index);
            if(compact()) (void)compressed_log_output(0x10400000u,empty_short,empty_short,index);
            break;
        }
        if(record[0x30u]==1u) {
            uint8_t mask=(uint8_t)((has_bytes(record+0x34u)?1u:0u)
                        |(has_bytes(record+0x50u)?2u:0u)
                        |(has_bytes(record+7u)?4u:0u)
                        |(has_bytes(record+0x1eu)?8u:0u));
            if(extended()) audio_log_extended(4u,module,source,function,0x15bu,mismatch,record[0x2eu],mask);
            if(compact()) (void)compressed_log_output(0x10800000u,mismatch_short,mismatch_short,record[0x2eu],mask);
            if(record[0x2eu]!=mask) {
                record[0x2eu]=mask;
                (void)audio_ble_privacy_rewrite_record(record);
            }
        }
        if(record[0x30u]==1u && record[0x2eu]!=0u) {
            (void)audio_queue_copy_bytes(destination,record,200u);
            destination[0x2fu]=1u;
            destination[0x30u]=1u;
            if(extended()) audio_log_extended(4u,module,source,function,0x16cu,irk,index,record[0x2eu]);
            if(compact()) (void)compressed_log_output(0x10800000u,irk_short,irk_short,index,record[0x2eu]);
            if((record[0x2eu]&4u)!=0u) audio_dump_hex(peer_irk,16u,destination+7u,16u);
            if(extended()) audio_log_extended(4u,module,source,function,0x176u,loaded,index,record[0x2eu],record[0x30u],destination[5],destination[4],destination[3],destination[2],destination[1],destination[0]);
            if(compact()) (void)compressed_log_output(0x12400000u,loaded_short,loaded_short,index,record[0x2eu],record[0x30u],destination[5],destination[4],destination[3],destination[2],destination[1],destination[0]);
            valid_count=(uint8_t)(valid_count+1u);
        } else {
            if(extended()) audio_log_extended(4u,module,source,function,0x17eu,skip,index,record[0x30u],record[0x2eu]);
            if(compact()) (void)compressed_log_output(0x10c00000u,skip_short,skip_short,index,record[0x30u],record[0x2eu]);
            clear_row(destination);
            destination[0x2fu]=0u;
            destination[0x30u]=0u;
        }
        destination+=200u;
    }
    if(extended()) audio_log_extended(4u,module,source,function,0x18du,summary,valid_count);
    if(compact()) (void)compressed_log_output(0x10400000u,summary_short,summary_short,valid_count);
}

/* Native AppDbNewRecord 0x47a71c and oldest-record lookup 0x47a6b4. */
#include <stdint.h>
extern uint8_t audio_ble_privacy_rows[10u*200u]; /* live RAM 0x20067a30 */
extern uint32_t audio_ble_pair_timestamp_counter_20074344;
extern uint8_t audio_ble_pair_count(uint8_t);
extern uint8_t DmHostAddrType(uint8_t);
extern void DmPrivRemDevFromResList(uint8_t,const uint8_t *,uint16_t);
extern void audio_ble_pair_record_clear_full(uint8_t *);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static uint32_t timestamp(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put_timestamp(uint8_t *p,uint32_t x){p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);p[2]=(uint8_t)(x>>16);p[3]=(uint8_t)(x>>24);}
uint8_t *audio_ble_pair_oldest_for_role_47a6b4(uint8_t role){
    uint8_t *oldest=0;
    uint32_t minimum=UINT32_MAX;
    for(uint32_t i=0;i<10u;i++){
        uint8_t *row=audio_ble_privacy_rows+i*200u;
        if(row[0x2fu]!=0u && row[0x30u]!=0u && row[0xc3u]==role){
            const uint32_t value=timestamp(row+0xc4u);
            if(value<minimum){minimum=value;oldest=row;}
        }
    }
    return oldest;
}
static const char module[]="ble.smpdb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function_name[]="AppDbNewRecord";
static void full_log(uint8_t role){
    static const char plain[]="Database full for role: %s. Deleting the oldest record.";
    static const char compact[]="[ble.smpdb]Database full for role: %s. Deleting the oldest record.";
    const char *name=role?"Master":"Slave";
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function_name,0x396u,plain,name);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,compact,compact,name);
}
static void no_slot_log(void){
    static const char plain[]="AppDbNewRecord: No free slots available in the entire database.";
    static const char compact[]="[ble.smpdb]AppDbNewRecord: No free slots available in the entire database.";
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function_name,0x3b3u,plain);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,compact,compact);
}
uint8_t *audio_ble_pair_record_create_47a71c(uint8_t type,const uint8_t *address,uint8_t role){
    if(audio_ble_pair_count(role)>4u){
        full_log(role);
        uint8_t *oldest=audio_ble_pair_oldest_for_role_47a6b4(role);
        if(oldest!=0){
            DmPrivRemDevFromResList(oldest[6],oldest,0u);
            audio_ble_pair_record_clear_full(oldest);
        }
    }
    for(uint32_t i=0;i<10u;i++){
        uint8_t *row=audio_ble_privacy_rows+i*200u;
        if(row[0x2fu]!=0u)continue;
        audio_uart_buffer_zero(row,200u,0u);
        row[0x2fu]=1u;
        row[6]=DmHostAddrType(type);
        (void)audio_queue_copy_bytes(row,address,6u);
        row[0xc3u]=role;
        put_timestamp(row+0xc4u,++audio_ble_pair_timestamp_counter_20074344);
        return row;
    }
    no_slot_log();
    return 0;
}

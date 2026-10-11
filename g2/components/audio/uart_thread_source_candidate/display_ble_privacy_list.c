/* Native AppLoadResList-like body 0x479418; ten 200-byte product rows. */
#include <stdint.h>
extern uint8_t audio_ble_privacy_rows[10u*200u]; /* live/product RAM 0x20067a30; loader ownership unresolved */
extern uint32_t audio_log_level(void); /* selected stock policy 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const uint8_t *DmSecGetLocalIrk(void); /* 0x4d2524 */
extern void DmPrivAddDevToResList(uint8_t,const uint8_t *,const uint8_t *,const uint8_t *,uint8_t,uint16_t); /* 0x4d282e */
extern void DmPrivSetAddrResEnable(uint8_t); /* 0x4d28cc */
static const uint8_t empty_irk[16]={0}; /* exact source literal at 0x784f90 */
static const char module[]="ble.smpdb"; /* 0x78a0d0 */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="AppLoadResList"; /* 0x784f60 */
static const char total_message[]="AppLoadResList totalValidRecords = %d"; /* 0x7477c4 */
static const char total_short[]="[ble.smpdb]AppLoadResList totalValidRecords = %d"; /* 0x726d20 */
static const char enable_message[]="AppLoadResList DmPrivSetAddrResEnable"; /* 0x7477ec */
static const char enable_short[]="[ble.smpdb]AppLoadResList DmPrivSetAddrResEnable"; /* 0x726d54 */
static int nonzero_irk(const uint8_t *p) {
    for(uint32_t i=0;i<16u;i++) if(p[i]!=empty_irk[i]) return 1;
    return 0;
}
void audio_ble_subsystem_child_479418(void) {
    uint8_t valid=0u;
    for(uint32_t i=0;i<10u;i++) {
        uint8_t *row=audio_ble_privacy_rows+i*200u;
        if(row[0x2fu]!=0u && row[0x30u]!=0u && nonzero_irk(row+7u))
            valid=(uint8_t)(valid+1u);
    }
    if((audio_log_level()&2u)!=0u)
        audio_log_extended(4u,module,source,function,0x115u,total_message,valid);
    uint32_t policy=audio_log_level();
    if((policy&1u)!=0u || (audio_log_level()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,total_short,total_short,valid);
    uint8_t added=0u;
    for(uint32_t i=0;i<10u;i++) {
        uint8_t *row=audio_ble_privacy_rows+i*200u;
        if(row[0x2fu]==0u || row[0x30u]==0u || !nonzero_irk(row+7u)) continue;
        row[0x2eu]|=4u;
        uint8_t last=(uint8_t)(added==(uint8_t)(valid-1u));
        const uint8_t *local_irk=DmSecGetLocalIrk();
        DmPrivAddDevToResList(row[0x1du],row+0x17u,row+7u,local_irk,last,0u);
        added=(uint8_t)(added+1u);
    }
    if(added!=0u) {
        DmPrivSetAddrResEnable(1u);
        if((audio_log_level()&2u)!=0u)
            audio_log_extended(4u,module,source,function,0x130u,enable_message);
        policy=audio_log_level();
        if((policy&1u)!=0u || (audio_log_level()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,enable_short,enable_short);
    }
}

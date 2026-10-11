/* Native APP_MasterSysStartTryConnectRing 0x4a23ac. */
#include <stdint.h>
extern const volatile uint8_t *const audio_uart_hand_context; /* 0x466010 -> 0x4667ec */
extern volatile uint8_t audio_ble_ring_link_state; /* RAM 0x20074f85 */
extern volatile uint16_t audio_ble_master_connect_wait; /* RAM 0x20074f18 */
extern uint32_t audio_uart_ring_active(void); /* 0x4a2914 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* 0x439be4 */
extern void audio_dump_hex(const char *,uint32_t,const uint8_t *,uint32_t); /* 0x43dacc */
extern void audio_ble_master_set_target(const uint8_t *,const char *,uint8_t); /* 0x4a2068 */
extern uint32_t audio_ble_master_auth_mode_set(uint8_t); /* 0x4a2168 */
extern void audio_ble_master_schedule_connect(uint32_t,uint8_t); /* 0x4a2618 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.master";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[]="APP_MasterSysStartTryConnectRing";
static const char name_seed[14]={'E','V','E','N',' ','R','1','\0','r','i','n','g','M','a'};
void audio_ble_master_start_try_connect_ring(void) {
    if(audio_uart_ring_active()==0u) {
        if(audio_log_level()&2u)
            audio_log_extended(3u,module,source,function,0x4d8u,
                "APP_MasterSysStartTryConnectRing: not ring owner role, skip");
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x0c000000u,
                "[ble.master]APP_MasterSysStartTryConnectRing: not ring owner role, skip",
                "[ble.master]APP_MasterSysStartTryConnectRing: not ring owner role, skip");
        return;
    }
    uint8_t address[6];
    char name[15];
    (void)audio_queue_copy_bytes(address,(const uint8_t *)audio_uart_hand_context+12u,6u);
    (void)audio_queue_copy_bytes(name,name_seed,14u);
    audio_dump_hex("ringMac",16u,address,6u);
    if(audio_log_level()&2u)
        audio_log_extended(3u,module,source,function,0x4e1u,
            "ringAddr = %02X:%02X:%02X:%02X:%02X:%02X",
            address[5],address[4],address[3],address[2],address[1],address[0]);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x0d800000u,
            "[ble.master]ringAddr = %02X:%02X:%02X:%02X:%02X:%02X",
            "[ble.master]ringAddr = %02X:%02X:%02X:%02X:%02X:%02X",
            address[5],address[4],address[3],address[2],address[1],address[0]);
    uint8_t unset=1u;
    for(uint32_t i=0;i<6u;i++) if(address[i]!=0xffu) unset=0u;
    if(unset!=0u) {
        if(audio_log_level()&2u)
            audio_log_extended(3u,module,source,function,0x4e3u,"ringMac is not set");
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x0c000000u,"[ble.master]ringMac is not set","[ble.master]ringMac is not set");
        return;
    }
    if(audio_ble_ring_link_state==3u) {
        if(audio_log_level()&2u)
            audio_log_extended(3u,module,source,function,0x4e7u,
                "APP_MasterSysStartTryConnectRing: LOCAL_DISCONNECTING, skip");
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x0c000000u,
                "[ble.master]APP_MasterSysStartTryConnectRing: LOCAL_DISCONNECTING, skip",
                "[ble.master]APP_MasterSysStartTryConnectRing: LOCAL_DISCONNECTING, skip");
        return;
    }
    name[14]='\0';
    if(audio_log_level()&2u)
        audio_log_extended(4u,module,source,function,0x4ebu,"ringName = %s",name);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,"[ble.master]ringName = %s","[ble.master]ringName = %s",name);
    audio_ble_master_set_target(address,name,15u);
    if(audio_log_level()&2u)
        audio_log_extended(4u,module,source,function,0x4edu,"TO CONNECT RING");
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10000000u,"[ble.master]TO CONNECT RING","[ble.master]TO CONNECT RING");
    (void)audio_ble_master_auth_mode_set(1u);
    audio_ble_master_connect_wait=0u;
    audio_ble_master_schedule_connect(2000u,0u);
}

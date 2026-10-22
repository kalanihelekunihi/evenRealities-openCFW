/* Native target setter 0x4a2068, auth-mode setter 0x4a2168, scheduler 0x4a2618. */
#include <stdint.h>
extern uint8_t audio_ble_master_target_address[6]; /* RAM 0x200003c0 */
extern char audio_ble_master_target_name[15]; /* RAM 0x200003c8 */
extern volatile uint8_t audio_ble_master_auth_mode; /* RAM 0x20074f80 */
extern volatile uint8_t audio_ble_master_connect_state; /* RAM 0x20074f87 */
extern void audio_ble_master_connect_event(void); /* 0x4a1b60 */
extern void audio_ble_master_cancel_retry(void); /* 0x4a17f4 */
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t); /* 0x47697e */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* 0x439be4 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.master";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[]="APP_MasterSetTargetAddrName";
void audio_ble_master_set_target(const uint8_t *address,const char *name,uint8_t name_length) {
    if(address!=0) {
        (void)audio_queue_copy_bytes(audio_ble_master_target_address,address,6u);
        if(audio_log_level()&2u)
            audio_log_extended(4u,module,source,function,0x478u,
                "_g_targetAddr = %02x:%02x:%02x:%02x:%02x:%02x",
                audio_ble_master_target_address[5],audio_ble_master_target_address[4],
                audio_ble_master_target_address[3],audio_ble_master_target_address[2],
                audio_ble_master_target_address[1],audio_ble_master_target_address[0]);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x11800000u,
                "[ble.master]_g_targetAddr = %02x:%02x:%02x:%02x:%02x:%02x",
                "[ble.master]_g_targetAddr = %02x:%02x:%02x:%02x:%02x:%02x",
                audio_ble_master_target_address[5],audio_ble_master_target_address[4],
                audio_ble_master_target_address[3],audio_ble_master_target_address[2],
                audio_ble_master_target_address[1],audio_ble_master_target_address[0]);
    }
    if(name!=0) {
        audio_uart_buffer_zero(audio_ble_master_target_name,15u,0u);
        (void)audio_queue_copy_bytes(audio_ble_master_target_name,name,name_length);
        if(audio_log_level()&2u)
            audio_log_extended(4u,module,source,function,0x47eu,
                "_g_targetName : %s",audio_ble_master_target_name);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x10400000u,
                "[ble.master]_g_targetName : %s",
                "[ble.master]_g_targetName : %s",audio_ble_master_target_name);
    }
}
/* Stock 0x004A2168 (auth_mode_set) */
uint32_t audio_ble_master_auth_mode_set(uint8_t mode) {
    if(mode<0x5au) audio_ble_master_auth_mode=mode;
    return audio_ble_master_auth_mode!=0u;
}
/* Stock 0x004A2618 (central_schedule_master_connect_004a2618) */
void audio_ble_master_schedule_connect(uint32_t delay,uint8_t use_alternate_event) {
    audio_ble_master_cancel_retry();
    audio_ble_master_connect_state=2u;
    uint32_t event=use_alternate_event?0x81u:1u;
    audio_event_loop_push_delayed(audio_ble_master_connect_event,event,delay);
}

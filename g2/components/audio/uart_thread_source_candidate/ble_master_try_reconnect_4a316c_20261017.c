/* Stock Main APP_MasterTryReconnectRingByScene, 0x4a316c. */
#include <stdint.h>

extern uint32_t audio_uart_ring_active(void); /* 0x4a2914 */
extern uint8_t *audio_setting_unit_record_get_466010(void);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint32_t audio_ble_master_is_connected_4a22c6(void);
extern volatile uint8_t audio_ble_master_connect_state; /* 0x20074f87 */
extern volatile uint8_t audio_ble_ring_link_state; /* 0x20074f85 */
extern volatile uint16_t audio_ble_master_connect_wait; /* 0x20074f18 */
extern const char *audio_ble_ring_link_state_name(uint8_t);
extern void audio_ble_master_cancel_retry(void);
extern void audio_ble_master_set_target_hand_4a2068(const void *,const void *,uint32_t);
extern uint32_t audio_ble_master_auth_mode_set(uint8_t);
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t);
extern void audio_ble_master_connect_event(void);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);

static const char module[]="ble.master";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function_name[]="APP_MasterTryReconnectRingByScene";
static const char name_seed[14]={'E','V','E','N',' ','R','1','\0','r','i','n','g','M','a'};

static void log_plain(uint32_t line,const char *message,const char *compact)
{
    if (audio_log_level() & 2u)
        audio_log_extended(3u,module,path,function_name,line,message);
    if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
        (void)compressed_log_output(0x0c000000u,compact,compact);
}
static void log_scene(uint32_t line,const char *message,const char *compact,uint8_t scene)
{
    if (audio_log_level() & 2u)
        audio_log_extended(3u,module,path,function_name,line,message,scene);
    if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
        (void)compressed_log_output(0x0c400000u,compact,compact,scene);
}

int32_t audio_uart_box_reconnect_attempt_4a316c(uint32_t scene_arg)
{
    uint8_t scene=(uint8_t)scene_arg;
    if (!audio_uart_ring_active()) {
        log_plain(0x60cu,"[Ring] TryReconnectByScene: not ring owner role, skip",
                  "[ble.master][Ring] TryReconnectByScene: not ring owner role, skip");
        return 0;
    }
    uint8_t address[6];
    (void)audio_queue_copy_bytes(address,audio_setting_unit_record_get_466010()+12u,6u);
    log_scene(0x613u,"[Ring] TryReconnectByScene: scene=%d",
              "[ble.master][Ring] TryReconnectByScene: scene=%d",scene);
    uint8_t unset=1u;
    for (uint32_t i=0;i<6u;i++) if (address[i]!=0xffu) unset=0u;
    if (unset) {
        log_plain(0x617u,"[Ring] Scene: ringMac not set, skip",
                  "[ble.master][Ring] Scene: ringMac not set, skip");
        return 0;
    }
    if (audio_ble_master_is_connected_4a22c6()) {
        log_plain(0x61cu,"[Ring] Scene: already connected, skip",
                  "[ble.master][Ring] Scene: already connected, skip");
        return 0;
    }
    if (audio_ble_master_connect_state==3u) {
        log_plain(0x621u,"[Ring] Scene: disconnect/unpair pending, skip",
                  "[ble.master][Ring] Scene: disconnect/unpair pending, skip");
        return 0;
    }
    uint8_t link=audio_ble_ring_link_state;
    if (link==1u) {
        log_plain(0x62au,"[Ring] Scene: OPENING in progress, skip",
                  "[ble.master][Ring] Scene: OPENING in progress, skip");
        return 0;
    }
    if (link==6u) {
        log_plain(0x62du,"[Ring] Scene: UNPAIRING in progress, skip",
                  "[ble.master][Ring] Scene: UNPAIRING in progress, skip");
        return 0;
    }
    if (link>=3u && link<=5u) {
        if (audio_log_level() & 2u)
            audio_log_extended(3u,module,path,function_name,0x632u,
                               "[Ring] Scene: state=%s, skip",audio_ble_ring_link_state_name(link));
        if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
            (void)compressed_log_output(0x0c400000u,
                "[ble.master][Ring] Scene: state=%s, skip",
                "[ble.master][Ring] Scene: state=%s, skip",
                audio_ble_ring_link_state_name(link));
        return 0;
    }
    uint32_t delay=scene==0u?1000u:500u;
    if (audio_ble_master_connect_wait>=11u) audio_ble_master_connect_wait=0u;
    audio_ble_master_cancel_retry();
    char name[15];
    (void)audio_queue_copy_bytes(name,name_seed,14u);
    name[14]='\0';
    audio_ble_master_set_target_hand_4a2068(address,name,15u);
    (void)audio_ble_master_auth_mode_set(1u);
    audio_ble_master_connect_state=1u;
    audio_event_loop_push_delayed(audio_ble_master_connect_event,1u,delay);
    if (audio_log_level() & 2u)
        audio_log_extended(3u,module,path,function_name,0x653u,
                           "[Ring] Scene %d: connect queued, delay=%lu ms state=%s",
                           scene,delay,audio_ble_ring_link_state_name(audio_ble_ring_link_state));
    if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
        (void)compressed_log_output(0x0cc00000u,
            "[ble.master][Ring] Scene %d: connect queued, delay=%lu ms state=%s",
            "[ble.master][Ring] Scene %d: connect queued, delay=%lu ms state=%s",
            scene,delay,audio_ble_ring_link_state_name(audio_ble_ring_link_state));
    return 1;
}

/* Native 0x4c4ee4, 0x472426, 0x46efd8 connected ring-touch follow-up. */
#include <stdint.h>
extern uint8_t *audio_ble_profile_connection_context; /* product pointer cell 0x2007432c */
extern int32_t audio_uart_ring_task_msg_send(uint32_t,const void *,uint32_t); /* ring_task_msg_send */
extern uint32_t audio_event_loop_remove_delayed(void (*)(void));
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t);
extern void audio_ble_phone_advertising_restart(void); /* callback 0x46ee70 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.ring";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ring.c";
static const char function[]="app_ring_enable_touch";
static const char event_name[]="RING_EnableTouchEvt";
uint8_t audio_ble_profile_get_connection_state(void) {
    return audio_ble_profile_connection_context[0x54u];
}
int32_t audio_ble_ring_touch_message(uint8_t enabled) {
    return (int8_t)audio_uart_ring_task_msg_send(0x80u,&enabled,1u);
}
void audio_ble_master_followup_delayed(void) {
    if(audio_log_level()&2u)
      audio_log_extended(4u,module,source,function,0xf0u,event_name);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x10000000u,"[task.ring]RING_EnableTouchEvt","[task.ring]RING_EnableTouchEvt");
    (void)audio_ble_ring_touch_message(1u);
    uint8_t connection=audio_ble_profile_get_connection_state();
    if(connection==0u) {
      if(audio_log_level()&2u)
        audio_log_extended(3u,module,source,function,0xf9u,
          "[Ring Connection] Touch enabled, restarting advertising for phone connection");
      if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x0c000000u,
          "[task.ring][Ring Connection] Touch enabled, restarting advertising for phone connection",
          "[task.ring][Ring Connection] Touch enabled, restarting advertising for phone connection");
      (void)audio_event_loop_remove_delayed(audio_ble_phone_advertising_restart);
      audio_event_loop_push_delayed(audio_ble_phone_advertising_restart,0u,500u);
    } else {
      if(audio_log_level()&2u)
        audio_log_extended(3u,module,source,function,0xfdu,
          "[Ring Connection] Touch enabled, phone already connected (connId=%d), no need to restart advertising",connection);
      if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x0c400000u,
          "[task.ring][Ring Connection] Touch enabled, phone already connected (connId=%d), no need to restart advertising",
          "[task.ring][Ring Connection] Touch enabled, phone already connected (connId=%d), no need to restart advertising",connection);
    }
}

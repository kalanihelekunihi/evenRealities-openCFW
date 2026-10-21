/* Native Main _thread_notify_event_handler 0x4c507e.
 * All event-bit branches and callback ordering follow the authenticated body. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_event_loop_remove_delayed(void (*)(void)); /* selected 0x476ace */
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t); /* selected 0x47697e */
extern void audio_uart_ring_msg_handler_4c4de8(void);
extern void audio_uart_ring_exit_4c53a6(void);
extern void audio_uart_ring_service_disc_followup_4c5032(void);
extern void audio_ble_master_followup_delayed(void); /* selected 0x4c4ee4 */
extern void audio_uart_ring_status_delayed_4a285c(void);
extern void audio_uart_ring_pair_enable_delayed_47257c(void);
extern void audio_uart_ring_pair_disable_delayed_472588(void);
extern void audio_uart_display_housekeep(void); /* selected 0x47243a */
extern uint32_t audio_settings_terminal_mode(void); /* native 0x46c630 */
extern void audio_uart_ring_mode_update_472362(uint16_t);
extern void audio_uart_ring_heartbeat_472244(void);
extern void audio_uart_ring_pair_mode_472546(void);

static const char module[]="task.ring";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ring.c";
static const char fn[]="_thread_notify_event_handler";
static const char notify[]="notifyValue = 0x%x";
static const char notify_short[]="[task.ring]notifyValue = 0x%x";
static const char disc[]="RING_TASK_MSG_SERVICE_DISC_CMPL_EVT";
static const char disc_short[]="[task.ring]RING_TASK_MSG_SERVICE_DISC_CMPL_EVT";
static const char disconnect[]="RING_TASK_MSG_DISCONNRECT_EVT";
static const char disconnect_short[]="[task.ring]RING_TASK_MSG_DISCONNRECT_EVT";
static const char pair[]="RING_TASK_MSG_PAIR_CMPL_EVT";
static const char pair_short[]="[task.ring]RING_TASK_MSG_PAIR_CMPL_EVT";
static const char heartbeat[]="RING_TASK_MSG_HEARTBEAT_EVT";
static const char heartbeat_short[]="[task.ring]RING_TASK_MSG_HEARTBEAT_EVT";
static const char enable_pair[]="RING_TASK_MSG_ENABLE_PAIR_EVT";
static const char enable_pair_short[]="[task.ring]RING_TASK_MSG_ENABLE_PAIR_EVT";
static const char reconnect[]="RING_TASK_MSG_RECONNECT_RING";
static const char reconnect_short[]="[task.ring]RING_TASK_MSG_RECONNECT_RING";
static const char enable_adv[]="RING_TASK_MSG_ENABLE_RING_ADV";
static const char enable_adv_short[]="[task.ring]RING_TASK_MSG_ENABLE_RING_ADV";

static uint32_t log_event(uint32_t line,const char *message,const char *short_message) {
    uint32_t extended=(audio_log_flags()&2u)!=0u;
    if(extended)
        audio_log_extended(4u,module,path,fn,line,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,short_message,short_message);
    return extended;
}
static void reschedule(void (*callback)(void),uint32_t ms) {
    (void)audio_event_loop_remove_delayed(callback);
    audio_event_loop_push_delayed(callback,0u,ms);
}
static void refresh_mode(void) {
    audio_uart_display_housekeep();
    audio_uart_ring_mode_update_472362(
        audio_settings_terminal_mode()==0u?1000u:500u);
}

uint32_t audio_uart_ring_notify_event_4c507e(uint32_t bits,uint32_t ambient_r1) {
    uint32_t result=ambient_r1;
    if((audio_log_flags()&2u)!=0u) {
        audio_log_extended(4u,module,path,fn,271u,notify,bits);
        result=271u;
    }
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,notify_short,notify_short,bits);
    if((bits&(1u<<22))!=0u)audio_uart_ring_msg_handler_4c4de8();
    if((bits&(1u<<2))!=0u) {
        if(log_event(281u,disc,disc_short))result=281u;
        reschedule(audio_uart_ring_service_disc_followup_4c5032,200u);
        reschedule(audio_ble_master_followup_delayed,500u);
        reschedule(audio_uart_ring_status_delayed_4a285c,3000u);
    }
    if((bits&(1u<<3))!=0u) {
        if(log_event(293u,disconnect,disconnect_short))result=293u;
    }
    if((bits&(1u<<4))!=0u) {
        if(log_event(300u,pair,pair_short))result=300u;
        reschedule(audio_ble_master_followup_delayed,200u);
        reschedule(audio_uart_ring_status_delayed_4a285c,3000u);
        refresh_mode();
    }
    if((bits&(1u<<5))!=0u) {
        if(log_event(317u,heartbeat,heartbeat_short))result=317u;
        audio_uart_ring_heartbeat_472244();
    }
    if((bits&(1u<<6))!=0u) {
        if(log_event(323u,enable_pair,enable_pair_short))result=323u;
        audio_uart_ring_pair_mode_472546();
        reschedule(audio_uart_ring_pair_enable_delayed_47257c,500u);
        reschedule(audio_uart_ring_pair_disable_delayed_472588,700u);
    }
    if((bits&(1u<<11))!=0u) {
        if(log_event(334u,reconnect,reconnect_short))result=334u;
        refresh_mode();
    }
    if((bits&(1u<<8))!=0u) {
        if(log_event(343u,enable_adv,enable_adv_short))result=343u;
    }
    if((bits&(1u<<23))!=0u)audio_uart_ring_exit_4c53a6();
    return result;
}

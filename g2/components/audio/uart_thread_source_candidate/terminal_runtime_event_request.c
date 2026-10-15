/* Apollo terminal_request_runtime_event_if_allowed, native 0x5e873e. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_mode; /* native RAM 0x2006e345 */
extern uint32_t audio_terminal_display_queue_handle; /* native RAM 0x20074a90 */
extern uint8_t audio_terminal_runtime_event_from_ble(uint8_t);
extern uint8_t audio_terminal_state_allows_runtime_event(uint32_t);
extern uint32_t audio_td_counter_b_get(void);
extern uint32_t audio_terminal_request_display(uint8_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

/* Native terminal RAM base 0x2006e0d0 plus offsets 0x277,0x27f,0x288. */
uint8_t audio_terminal_runtime_flag_277;
uint8_t audio_terminal_runtime_flag_27f;
uint32_t audio_terminal_runtime_saved_session;

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_request_runtime_event_if_allowed";
static const char dropped[]="drop runtime query notification in state=%d session=%lu";
static const char dropped_short[]="[terminal.pb]drop runtime query notification in state=%d session=%lu";

void audio_terminal_request_runtime_event_if_allowed(uint32_t ble_status) {
    uint8_t event=audio_terminal_runtime_event_from_ble((uint8_t)ble_status);
    uint8_t mode=audio_terminal_ui_mode;
    if(event!=22u) {
        (void)audio_terminal_request_display(event,0u);
        return;
    }
    if(mode==0u || audio_terminal_display_queue_handle==0u) {
        if(audio_terminal_runtime_saved_session==0u)
            audio_terminal_runtime_saved_session=audio_td_counter_b_get();
        audio_terminal_runtime_flag_277=0u;
        audio_terminal_runtime_flag_27f=0u;
        (void)audio_terminal_request_display(event,audio_terminal_runtime_saved_session);
        return;
    }
    if(audio_terminal_state_allows_runtime_event(mode)!=0u) {
        (void)audio_terminal_request_display(event,audio_terminal_runtime_saved_session);
        return;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,236u,dropped,
                           mode,audio_terminal_runtime_saved_session);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08800000u,dropped_short,dropped_short,
                                    mode,audio_terminal_runtime_saved_session);
}

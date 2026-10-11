/* Native _connectParamReq_impl 0x47720c: connection profile arbitration,
 * duplicate backoff and WSF event submission. */
#include <stdint.h>
extern void *audio_ble_dm_conn_params(void); /* native 0x46efcc */
extern uint8_t *audio_ble_cached_conn_params; /* pointer cell RAM 0x2007433c */
extern volatile uint8_t audio_ble_connect_request_pending; /* RAM 0x20074f91 */
extern volatile uint8_t audio_ble_current_conn_mode; /* RAM 0x20004542 */
extern volatile uint8_t audio_ble_requested_conn_mode; /* RAM 0x20004541 */
extern volatile uint8_t audio_ble_connect_event_handler; /* RAM 0x20074f8e */
extern uint32_t audio_ble_is_conn_params_slow(const void *); /* native 0x476fe2 */
extern uint32_t audio_ble_is_conn_params_fast(const void *); /* native 0x476db8 */
extern uint32_t audio_event_loop_remove_delayed(void (*)(void)); /* native 0x476ace */
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t); /* native 0x47697e */
extern void audio_ble_connect_param_request(uint8_t); /* native 0x47761c */
extern void *audio_wsf_msg_alloc(uint16_t); /* native 0x4bf99e */
extern void audio_wsf_msg_send(uint8_t,void *); /* native 0x4bf9ba */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.param";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_connect_params.c";
static const char function[]="_connectParamReq_impl";
static const char invalid[]="_connectParamReq_impl: invalid pCb(%p) or connId, skip";
static const char invalid_short[]="[ble.param]_connectParamReq_impl: invalid pCb(%p) or connId, skip";
static const char mode_message[]="conn_params mode %d actural(%d) hope(%d)";
static const char mode_short[]="[ble.param]conn_params mode %d actural(%d) hope(%d)";
static const char interval[]="connInterval = %d ms";
static const char interval_short[]="[ble.param]connInterval = %d ms";
static const char latency[]="connLatency = %d";
static const char latency_short[]="[ble.param]connLatency = %d";
static const char timeout[]="supTimeout = %d ms";
static const char timeout_short[]="[ble.param]supTimeout = %d ms";
static const char slow_message[]="conn_params mode %d hope Slow ResultStatus(%d) actural(%d)";
static const char slow_short[]="[ble.param]conn_params mode %d hope Slow ResultStatus(%d) actural(%d)";
static const char fast_message[]="conn_params mode %d hope Fast ResultStatus(%d) actural(%d)";
static const char fast_short[]="[ble.param]conn_params mode %d hope Fast ResultStatus(%d) actural(%d)";
static const char duplicate[]="conn_params update already in progress, delay duplicate request. mode=%d";
static const char duplicate_short[]="[ble.param]conn_params update already in progress, delay duplicate request. mode=%d";
static const char update[]="conn_params need updata mode to %d";
static const char update_short[]="[ble.param]conn_params need updata mode to %d";
static uint16_t half(const uint8_t *p,uint32_t n) {return (uint16_t)p[n]|(uint16_t)((uint16_t)p[n+1u]<<8);}
static void log_one(uint8_t severity,uint32_t line,uint32_t mask,uint32_t prefix,
                    const char *text,const char *short_text,uint32_t value) {
    if((audio_log_flags()&2u)!=0u)audio_log_extended(severity,module,path,function,line,text,value);
    if((audio_log_flags()&mask)!=0u)(void)compressed_log_output(prefix,short_text,short_text,value);
}
static void log_three(uint32_t line,const char *text,const char *short_text,
                      uint32_t a,uint32_t b,uint32_t c) {
    if((audio_log_flags()&2u)!=0u)audio_log_extended(4u,module,path,function,line,text,a,b,c);
    if((audio_log_flags()&5u)!=0u)(void)compressed_log_output(0x10c00000u,short_text,short_text,a,b,c);
}
void audio_ble_connect_param_request_impl(uint8_t mode) {
    uint8_t *conn=(uint8_t *)audio_ble_dm_conn_params();
    if(conn==0||conn[4u]==0u||conn[4u]>3u) {
        log_one(2u,237u,5u,0x08400000u,invalid,invalid_short,(uint32_t)(uintptr_t)conn);
        audio_ble_connect_request_pending=0u;
        return;
    }
    uint8_t *cached=audio_ble_cached_conn_params;
    log_three(242u,mode_message,mode_short,mode,audio_ble_current_conn_mode,
              audio_ble_requested_conn_mode);
    uint32_t milliseconds=((uint32_t)half(cached,24u)*1250u)/1000u;
    log_one(4u,243u,5u,0x10400000u,interval,interval_short,milliseconds);
    log_one(4u,244u,5u,0x10400000u,latency,latency_short,half(cached,26u));
    log_one(4u,245u,5u,0x10400000u,timeout,timeout_short,
            ((uint32_t)half(cached,28u)*10000u)/1000u);
    if(mode==0xa4u) {
        uint8_t status=(uint8_t)audio_ble_is_conn_params_slow(cached);
        log_three(248u,slow_message,slow_short,mode,audio_ble_current_conn_mode,status);
        if(status==0xa4u) {audio_ble_current_conn_mode=0xa4u;return;}
    } else if(mode==0xa3u) {
        uint8_t status=(uint8_t)audio_ble_is_conn_params_fast(cached);
        log_three(255u,fast_message,fast_short,mode,audio_ble_current_conn_mode,status);
        if(status==0xa3u) {
            audio_ble_current_conn_mode=0xa3u;
            audio_ble_connect_request_pending=0u;
            return;
        }
    }
    if(audio_ble_connect_request_pending!=0u&&mode==audio_ble_requested_conn_mode) {
        log_one(4u,265u,5u,0x10400000u,duplicate,duplicate_short,mode);
        audio_ble_connect_request_pending=0u;
        (void)audio_event_loop_remove_delayed((void (*)(void))audio_ble_connect_param_request);
        audio_event_loop_push_delayed((void (*)(void))audio_ble_connect_param_request,mode,10000u);
        return;
    }
    log_one(4u,272u,5u,0x10400000u,update,update_short,mode);
    audio_ble_connect_request_pending=1u;
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(12u);
    if(message!=0) {
        message[2]=mode;
        message[0]=conn[4u];message[1]=0u;
        audio_wsf_msg_send(audio_ble_connect_event_handler,message);
    }
}

/* Native _connectParamReq 0x47761c: peripheral handler and DM gating. */
#include <stdint.h>
extern uint8_t audio_ble_controller[]; /* direct product struct 0x200727f0, native getter returns address */
extern void *audio_ble_dm_conn_params(void); /* native dmGetConnParamPtr 0x46efcc */
extern uint32_t audio_settings_terminal_mode(void); /* native 0x46c630 */
extern void *audio_wsf_msg_alloc(uint16_t); /* native WsfMsgAlloc 0x4bf99e */
extern void audio_wsf_msg_send(uint8_t,void *); /* native WsfMsgSend 0x4bf9ba */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.param";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_connect_params.c";
static const char function[]="_connectParamReq";
static const char no_handler[]="_connectParamReq: pBleCb or handlerId is NULL";
static const char no_handler_short[]="[ble.param]_connectParamReq: pBleCb or handlerId is NULL";
static const char no_conn[]="_connectParamReq: no active slave connection, skip";
static const char no_conn_short[]="[ble.param]_connectParamReq: no active slave connection, skip";
static const char terminal[]="terminal mode is 1, skip slow mode";
static const char terminal_short[]="[ble.param]terminal mode is 1, skip slow mode";
static void log_skip(uint8_t severity,uint32_t line,uint32_t compressed,
                     const char *message,const char *short_message) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(severity,module,path,function,line,message);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(compressed,short_message,short_message);
}
void audio_ble_connect_param_request(uint8_t mode) {
    uint8_t *controller=audio_ble_controller;
    if(controller==0||controller[0x56u]==0u) {
        log_skip(1u,288u,0x04000000u,no_handler,no_handler_short);
        return;
    }
    if(audio_ble_dm_conn_params()==0) {
        log_skip(2u,293u,0x08000000u,no_conn,no_conn_short);
        return;
    }
    if(audio_settings_terminal_mode()==1u&&mode==0xa4u) {
        log_skip(2u,298u,0x08000000u,terminal,terminal_short);
        return;
    }
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(12u);
    if(message!=0) {
        message[2]=0xb9u;
        message[0]=0u;message[1]=0u;
        message[8]=mode;message[9]=0u;
        audio_wsf_msg_send(controller[0x56u],message);
    }
}

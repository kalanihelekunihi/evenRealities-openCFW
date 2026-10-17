/* Stock Main BoxDetect_ReceiveCaseInfoFromPeer, 0x4ac890. */
#include <stdint.h>
extern uint8_t audio_uart_device_role_get(void);
extern volatile uint8_t audio_uart_case_peer_raw_20074188[4];
extern volatile uint8_t audio_uart_case_soc_cell_2007418c;
extern volatile uint8_t audio_uart_case_charge_cell_2007418d;
extern volatile uint8_t audio_uart_case_sensor_b;
extern volatile uint8_t audio_uart_case_sensor_a;
extern volatile uint8_t audio_uart_case_status_disabled;
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_service_nonce(uint8_t out[4]);
extern void audio_uart_case_display_refresh_4abf86(void);
extern void audio_uart_case_notify_4abec8(void);
extern void audio_uart_service_prepare3(uint32_t);
extern void audio_uart_display_housekeep(void);
extern void audio_uart_case_in_case_side_effect_5130a6(void);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="box.detect";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\box_detect\\service_box_detect.c";
static const char function_name[]="BoxDetect_ReceiveCaseInfoFromPeer";

static void log_plain(uint8_t level,uint32_t line,const char *message,const char *compact)
{
    if (audio_log_level() & 2u)
        audio_log_extended(level,module,path,function_name,line,message);
    if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
        (void)compressed_log_output((uint32_t)level<<26u,compact,compact);
}

void audio_uart_case_sync_response_4ac890(const uint8_t *message)
{
    if (message==0) {
        log_plain(1u,0x267u,"Invalid case sync message",
                  "[box.detect]Invalid case sync message");
        return;
    }
    if (audio_log_level() & 2u)
        audio_log_extended(4u,module,path,function_name,0x26cu,
            "Receive case sync from peer: msg_id=%d, soc=%d, charging=%d, lid=%d, in_case=%d",
            message[0],message[4],message[5],message[6],message[7]);
    if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
        (void)compressed_log_output(0x11400000u,
            "[box.detect]Receive case sync from peer: msg_id=%d, soc=%d, charging=%d, lid=%d, in_case=%d",
            "[box.detect]Receive case sync from peer: msg_id=%d, soc=%d, charging=%d, lid=%d, in_case=%d",
            message[0],message[4],message[5],message[6],message[7]);
    (void)audio_uart_device_role_get();
    for (uint32_t i=0;i<4u;i++) audio_uart_case_peer_raw_20074188[i]=message[4u+i];
    uint8_t state[4];
    audio_uart_buffer_zero(state,4u,0u);
    (void)audio_uart_service_nonce(state);
    if (state[0]>=message[4]) state[0]=message[4];
    state[1]=(state[1]!=0u && message[5]!=0u) ? 1u : 0u;
    state[2]=(state[2]==1u && message[6]==1u) ? 1u : 0u;
    state[3]=(state[3]==1u && message[7]==1u) ? 1u : 0u;
    uint8_t changed=0u;
    if (audio_uart_case_soc_cell_2007418c!=state[0]) {
        audio_uart_case_soc_cell_2007418c=state[0];changed=1u;
    }
    if (audio_uart_case_charge_cell_2007418d!=state[1]) {
        audio_uart_case_charge_cell_2007418d=state[1];changed=1u;
    }
    if (audio_uart_case_sensor_b!=state[2]) {
        audio_uart_case_sensor_b=state[2];changed=1u;
    }
    if (audio_uart_case_sensor_a!=state[3]) {
        audio_uart_case_sensor_a=state[3];changed=1u;
        if (audio_uart_case_status_disabled==0u) {
            audio_uart_case_display_refresh_4abf86();
            if (state[3]==1u) audio_uart_case_in_case_side_effect_5130a6();
            audio_uart_display_housekeep();
        } else {
            log_plain(3u,0x29eu,"force out box enabled, skip in-case side effects",
                      "[box.detect]force out box enabled, skip in-case side effects");
        }
    }
    if (changed) audio_uart_case_notify_4abec8();
    if (message[0]==3u) audio_uart_service_prepare3(2u);
}

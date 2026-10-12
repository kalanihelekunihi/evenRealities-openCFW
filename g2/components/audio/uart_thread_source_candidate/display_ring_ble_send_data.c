/* Native APP_BleRingSendDataMsg 0x4c4b7e, connection gate and Cordio
 * payload descriptor. The message's other allocated bytes remain untouched. */
#include <stdint.h>
struct audio_ble_ring_handler_state {uint8_t active;uint8_t handler;uint16_t reserved;
                                     uint16_t *service_handles;uint16_t initialized;};
extern struct audio_ble_ring_handler_state audio_ble_ring_handler_state; /* RAM 0x20074074 */
extern void audio_ble_tx_ready_wait(void); /* native 0x4d0b64 */
extern void audio_ble_tx_complete_notify(void); /* native 0x4d0c36 */
extern void *audio_wsf_msg_alloc(uint16_t); /* selected 0x4bf99e */
extern void audio_wsf_msg_send(uint8_t,void *); /* selected 0x4bf9ba */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.ring";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ring\\profile_ring.c";
static const char fn[]="APP_BleRingSendDataMsg";
static const char skipped[]="APP_BleRingSendDataMsg skipped: connId=%d, txHdl=0x%04X";
static const char skipped_short[]="[ble.ring]APP_BleRingSendDataMsg skipped: connId=%d, txHdl=0x%04X";
static const char alloc_failed[]="APP_BleRingSendDataMsg WsfMsgAlloc failed";
static const char alloc_failed_short[]="[ble.ring]APP_BleRingSendDataMsg WsfMsgAlloc failed";
uint32_t audio_uart_ring_ble_send_data_4c4b7e(const void *data,uint32_t length) {
    struct audio_ble_ring_handler_state *state=&audio_ble_ring_handler_state;
    if(state->active==0u || state->service_handles==0 || state->service_handles[0]==0u) {
        uint32_t tx=state->service_handles==0?0u:state->service_handles[0];
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,fn,327u,skipped,state->active,tx);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08800000u,skipped_short,skipped_short,
                                        state->active,tx);
        return 0u;
    }
    audio_ble_tx_ready_wait();
    uint8_t *msg=(uint8_t *)audio_wsf_msg_alloc(12u);
    if(msg==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,fn,339u,alloc_failed);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,alloc_failed_short,alloc_failed_short);
        audio_ble_tx_complete_notify();
    } else {
        msg[2]=0xacu;
        *(uint16_t *)(void *)msg=state->active;
        *(const void **)(void *)(msg+4u)=data;
        *(uint16_t *)(void *)(msg+8u)=(uint16_t)length;
        audio_wsf_msg_send(state->handler,msg);
    }
    return 0u;
}

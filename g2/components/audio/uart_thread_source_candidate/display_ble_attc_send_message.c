/* Native Cordio attcSendMsg at 0x4b5640. */
#include <stdint.h>
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
extern uint8_t *audio_ble_attc_ccb_by_conn_id_531820(uint8_t,uint8_t);
extern void audio_ble_attc_exec_callback_531ad6(uint8_t,uint8_t,uint16_t,uint8_t);
extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgSend(uint8_t,void *);
extern void audio_ble_wsf_message_free(void *);
extern uint8_t audio_ble_att_common_state[]; /* selected state at RAM 0x200610ac */
void *audio_ble_attc_send_message_4b5640(uint8_t connection,uint16_t handle,
                                           uint8_t operation,void *packet,uint8_t option) {
    uint16_t mtu=0u;
    uint8_t blocked=0u;
    WsfTaskLock();
    uint8_t *ccb=audio_ble_attc_ccb_by_conn_id_531820(connection,0u);
    if(ccb!=0) {
        uint32_t context=(uint32_t)ccb[0]|((uint32_t)ccb[1]<<8)|
                         ((uint32_t)ccb[2]<<16)|((uint32_t)ccb[3]<<24);
        const uint8_t *link=(const uint8_t *)(uintptr_t)context;
        mtu=(uint16_t)link[0]|((uint16_t)link[1]<<8);
        blocked=(uint8_t)((link[2]>>2u)&1u);
    }
    WsfTaskUnlock();
    if(mtu!=0u) {
        if(blocked!=0u) {
            audio_ble_attc_exec_callback_531ad6(connection,operation,handle,0x71u);
        } else {
            uint16_t length=0u;
            if(packet!=0) {
                if(operation==11u) {
                    if(option==0u) {
                        const uint8_t *nested=*(const uint8_t *const *)packet;
                        length=(uint16_t)(((uint16_t)nested[0]|((uint16_t)nested[1]<<8))+5u);
                    }
                } else {
                    const uint8_t *bytes=(const uint8_t *)packet;
                    length=(uint16_t)bytes[0]|((uint16_t)bytes[1]<<8);
                }
            }
            if(mtu<length) {
                audio_ble_attc_exec_callback_531ad6(connection,operation,handle,0x77u);
            } else {
                uint8_t *message=(uint8_t *)WsfMsgAlloc(12u);
                if(message!=0) {
                    *(uint16_t *)(void *)(message+0u)=connection;
                    message[2u]=operation;
                    message[3u]=option;
                    *(void **)(void *)(message+4u)=packet;
                    *(uint16_t *)(void *)(message+8u)=handle;
                    message[10u]=0u;
                    WsfMsgSend(audio_ble_att_common_state[0x60u],message);
                    return packet;
                }
            }
        }
    }
    if(packet!=0)audio_ble_wsf_message_free(packet);
    return packet;
}

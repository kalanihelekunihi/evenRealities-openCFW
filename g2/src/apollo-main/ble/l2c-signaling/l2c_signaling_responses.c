/* Native Cordio L2CAP allocation and signaling responses 0x530b28,
 * 0x530ae0 and 0x537230. R3 is the allocated message pointer in the
 * original call to L2cDataReq, so it is explicit in this C source. */
#include <stdint.h>
extern uint8_t *WsfMsgDataAlloc(uint16_t,uint8_t);
extern void L2cDataReq(uint16_t,uint16_t,uint16_t,uint8_t *);
uint8_t *audio_ble_l2c_msg_alloc_530b28(uint16_t total){
    return WsfMsgDataAlloc(total,0u);
}
static void send(uint8_t code,uint16_t handle,uint8_t id,uint16_t result){
    uint8_t *packet=audio_ble_l2c_msg_alloc_530b28(14u);
    if(packet==0)return;
    packet[8]=code;packet[9]=id;packet[10]=2u;packet[11]=0u;
    packet[12]=(uint8_t)result;packet[13]=(uint8_t)(result>>8);
    L2cDataReq(5u,handle,6u,packet);
}
void audio_ble_l2c_send_cmd_reject_530ae0(uint16_t handle,uint8_t id,uint16_t reason){
    send(1u,handle,id,reason);
}
void audio_ble_l2c_dm_conn_update_rsp_537230(uint8_t id,uint16_t handle,uint16_t result){
    send(0x13u,handle,id,result);
}

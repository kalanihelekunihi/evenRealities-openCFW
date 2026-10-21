/* Native SecAes 0x536426 and token child 0x5363fc; pinned Cordio sec_aes.c. */
#include <stdint.h>
extern uint8_t audio_ble_stack_state_20072cb8[];
extern void *WsfMsgAlloc(uint16_t length);
extern void WsfMsgEnq(void *queue,uint8_t handler,void *message);
extern void HciLeEncryptCmd(uint8_t *key,uint8_t *plain);

static uint8_t sec_next_token(void)
{
    uint8_t *const state=audio_ble_stack_state_20072cb8;
    uint8_t token=state[0x38u]++;
    if (token==0xffu) token=state[0x38u]++;
    return token;
}

uint8_t SecAes(uint8_t *key,uint8_t *plain,uint8_t handler,
               uint16_t connection,uint8_t event)
{
    uint8_t *message=WsfMsgAlloc(0x38u);
    if (!message) return 0xffu;
    message[3u]=sec_next_token();
    message[0u]=(uint8_t)connection;
    message[1u]=(uint8_t)(connection>>8u);
    message[2u]=event;
    message[0x34u]=0u;
    WsfMsgEnq(audio_ble_stack_state_20072cb8+0x20u,handler,message);
    HciLeEncryptCmd(key,plain);
    return message[3u];
}

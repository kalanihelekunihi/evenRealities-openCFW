/* Native SecLeEncryptCmd 0x5363ae, pinned Cordio sec_main.c. */
#include <stdint.h>
extern uint8_t audio_ble_stack_state_20072cb8[]; /* secCb base RAM */
extern void WStrReverseCpy(uint8_t *destination,const uint8_t *source,uint16_t length);
extern void WsfMsgEnq(void *queue,uint8_t handler,void *buffer);
extern void HciLeEncryptCmd(const uint8_t *key,const uint8_t *plain);
void SecLeEncryptCmd(const uint8_t *key,const uint8_t *plain,
                     void *buffer,uint8_t handler) {
    uint8_t reversed_key[16];
    uint8_t reversed_plain[16];
    WStrReverseCpy(reversed_key,key,16u);
    WStrReverseCpy(reversed_plain,plain,16u);
    WsfMsgEnq(audio_ble_stack_state_20072cb8+0x20u,handler,buffer);
    HciLeEncryptCmd(reversed_key,reversed_plain);
}

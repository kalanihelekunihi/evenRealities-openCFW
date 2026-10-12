/* Native SecCmac 0x53665c, pinned Cordio sec_cmac_hci.c request producer. */
#include <stdint.h>
extern void *WsfMsgAlloc(uint16_t size);
extern void Calc128Cpy(uint8_t *destination,uint8_t *source);
extern void secCmacGenSubkey1(void *queue_buffer); /* native 0x53653a */
extern volatile uint8_t audio_ble_stack_state_20072cb8[]; /* live secCb RAM */
uint8_t SecCmac(const uint8_t *key,uint8_t *text,uint16_t length,
                uint8_t handler,uint16_t connection,uint8_t event) {
    uint8_t *buffer=WsfMsgAlloc(100u);
    if (buffer==0) return 0u;
    *(uint8_t **)(void *)(buffer+0x30u)=buffer+0x38u;
    buffer[0x34u]=1u;
    buffer[3u]=audio_ble_stack_state_20072cb8[0x38u];
    audio_ble_stack_state_20072cb8[0x38u]=
        (uint8_t)(audio_ble_stack_state_20072cb8[0x38u]+1u);
    *(uint16_t *)(void *)(buffer+0u)=connection;
    buffer[2u]=event;
    *(uint8_t **)(void *)(buffer+0x38u)=text;
    *(uint16_t *)(void *)(buffer+0x5eu)=length;
    *(uint16_t *)(void *)(buffer+0x5cu)=0u;
    buffer[0x60u]=handler;
    buffer[0x61u]=0u;
    Calc128Cpy(buffer+0x3cu,(uint8_t *)(uintptr_t)key);
    secCmacGenSubkey1(buffer);
    return 1u;
}

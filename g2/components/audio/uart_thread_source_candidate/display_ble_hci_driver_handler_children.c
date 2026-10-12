/* Direct children of native HciDrvHandler 0x4b4ab2. */
#include <stdint.h>
extern void *audio_wsf_msg_alloc(uint16_t); /* selected WsfMsgAlloc 0x4bf99e */
extern void audio_ble_hci_cmd_send(void *); /* hciCmdSend selected 0x52ae5e */
extern void audio_ble_wsf_timer_insert(void *,uint32_t); /* 0x52a424 */
extern void audio_ble_hci_radio_scheduler_53006c(void *,const void *,uint32_t,uint32_t);
extern void audio_delay_us(uint32_t); /* selected 0x4807a0 */
void audio_ble_hci_boot_delay_491102(uint32_t microseconds) {
    audio_delay_us(microseconds);
}
void *audio_ble_hci_cmd_alloc_52ae38(uint16_t opcode,uint16_t length) {
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc((uint16_t)(length+3u));
    if(message!=0) {
        message[0]=(uint8_t)opcode;
        message[1]=(uint8_t)(opcode>>8u);
        message[2]=(uint8_t)length;
    }
    return message;
}
void audio_ble_hci_read_buf_size_cmd_52b620(void) {
    void *command=audio_ble_hci_cmd_alloc_52ae38(0x1001u,0u);
    if(command!=0)audio_ble_hci_cmd_send(command);
}
void WsfTimerStartMs(void *timer,uint32_t milliseconds) {
    audio_ble_wsf_timer_insert(timer,milliseconds/10u);
}
void audio_ble_hci_driver_empty_queue_4b4d18(void) {
    audio_ble_hci_radio_scheduler_53006c((void *)(uintptr_t)0x20073ba8u,
        (const void *)(uintptr_t)0x20065a10u,0x104u,0x820u);
}
uint64_t audio_ble_hci_ring_consume_5300e2(void *ring,void *output,uint32_t count) {
    volatile uint8_t *r=(volatile uint8_t *)ring;
    uint32_t word=0u;
    for(uint32_t i=0;i<4u;i++)word|=(uint32_t)r[0x10u+i]<<(i*8u);
    uint32_t bytes=word*count;
    uint32_t primask;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(primask) :: "memory");
    uint32_t available=0u;
    for(uint32_t i=0;i<4u;i++)available|=(uint32_t)r[8u+i]<<(i*8u);
    uint32_t accepted=0u;
    if(available>=bytes) {
        uint8_t *dst=(uint8_t *)output;
        uint32_t position=0u,capacity=0u,base=0u;
        for(uint32_t i=0;i<4u;i++) {
            position|=(uint32_t)r[4u+i]<<(i*8u);
            capacity|=(uint32_t)r[0xcu+i]<<(i*8u);
            base|=(uint32_t)r[0x14u+i]<<(i*8u);
        }
        for(uint32_t i=0;i<bytes;i++) {
            if(dst!=0)dst[i]=((const uint8_t *)(uintptr_t)base)[position];
            position=(position+1u)%capacity;
        }
        available-=bytes;
        for(uint32_t i=0;i<4u;i++) {
            r[4u+i]=(uint8_t)(position>>(i*8u));
            r[8u+i]=(uint8_t)(available>>(i*8u));
        }
        accepted=1u;
    }
    uint32_t control;
    __asm__ volatile("mrs %0, control" : "=r"(control));
    if((control&1u)==0u)
        __asm__ volatile("msr primask, %0" :: "r"(primask) : "memory");
    return ((uint64_t)primask<<32)|accepted;
}

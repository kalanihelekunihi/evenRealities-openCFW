#include <stdint.h>

extern uint32_t case_tick_word2(void);
extern uint32_t case_wait_condition(void *uart,uint32_t flag,uint32_t expected,
                                     uint32_t start,uint32_t timeout);

/* Original 0x080066ac. The UART handle and peripheral register window must
 * be live. Tick and wait helpers are separate lower contracts. */
/* Stock 0x080066AC (case_write_controller_blocking) */
uint32_t case_write_controller_blocking(void *handle,const uint8_t *data,
                                         uint32_t length,uint32_t timeout)
{
    volatile uint8_t *h=(volatile uint8_t *)handle;
    volatile uint32_t *tx_state=(volatile uint32_t *)(h+0x88u);
    if(*tx_state!=0x20u)return 2u;
    uint32_t cr1=*(volatile uint32_t *)(h+8u);
    uint32_t parity=*(volatile uint32_t *)(h+16u);
    if(!data || length==0u ||
       (cr1==0x1000u && parity==0u && ((uintptr_t)data&1u)))return 1u;
    *(volatile uint32_t *)(h+0x90u)=0u;
    *tx_state=0x21u;
    uint32_t start=case_tick_word2();
    *(volatile uint16_t *)(h+0x54u)=(uint16_t)length;
    *(volatile uint16_t *)(h+0x56u)=(uint16_t)length;
    uint32_t nine=(cr1==0x1000u && parity==0u);
    const uint8_t *byte=data;
    const uint16_t *half=(const uint16_t *)(const void *)data;
    volatile uint32_t *tdr=(volatile uint32_t *)(uintptr_t)
        (*(volatile uint32_t *)h+0x28u);
    while(*(volatile uint16_t *)(h+0x56u)!=0u){
        if(case_wait_condition(handle,0x80u,0u,start,timeout)!=0u)return 3u;
        if(nine){*tdr=(uint32_t)(*half&0x1ffu);half++;}
        else{*tdr=*byte;byte++;}
        (*(volatile uint16_t *)(h+0x56u))--;
    }
    if(case_wait_condition(handle,0x40u,0u,start,timeout)!=0u)return 3u;
    *tx_state=0x20u;
    return 0u;
}

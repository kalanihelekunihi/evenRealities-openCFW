#include <stdint.h>

extern uint32_t case_tick_word2(void);
extern uint32_t case_wait_condition(void *uart,uint32_t flag,uint32_t expected,
                                     uint32_t start,uint32_t timeout);

/* Original 0x080063ec. Caller supplies live UART/peripheral state and a
 * writable buffer; the tick/wait helpers are distinct source contracts. */
uint32_t case_bulk_receive(void *handle,uint8_t *buffer,uint32_t length,
                            uint32_t timeout)
{
    volatile uint8_t *h=(volatile uint8_t *)handle;
    volatile uint32_t *rx_state=(volatile uint32_t *)(h+0x8cu);
    if(*rx_state!=0x20u)return 2u;
    uint32_t cr1=*(volatile uint32_t *)(h+8u);
    uint32_t parity=*(volatile uint32_t *)(h+16u);
    if(!buffer || length==0u ||
       (cr1==0x1000u && parity==0u && ((uintptr_t)buffer&1u)))return 1u;
    *(volatile uint32_t *)(h+0x90u)=0u;
    *rx_state=0x22u;
    *(volatile uint32_t *)(h+0x6cu)=0u;
    uint32_t start=case_tick_word2();
    *(volatile uint16_t *)(h+0x5cu)=(uint16_t)length;
    *(volatile uint16_t *)(h+0x5eu)=(uint16_t)length;
    uint32_t mask;
    if(cr1==0x1000u)mask=parity==0u?0x1ffu:0xffu;
    else if(cr1==0u)mask=parity==0u?0xffu:0x7fu;
    else if(cr1==0x10000000u)mask=parity==0u?0x7fu:0x3fu;
    else mask=0u;
    *(volatile uint16_t *)(h+0x60u)=(uint16_t)mask;
    uint32_t nine=(cr1==0x1000u && parity==0u);
    volatile uint32_t *rdr=(volatile uint32_t *)(uintptr_t)
        (*(volatile uint32_t *)h+0x24u);
    while(*(volatile uint16_t *)(h+0x5eu)!=0u){
        if(case_wait_condition(handle,0x20u,0u,start,timeout)!=0u)return 3u;
        uint32_t value=*rdr&mask;
        if(nine){*(uint16_t *)(void *)buffer=(uint16_t)value;buffer+=2;}
        else{*buffer=(uint8_t)value;buffer++;}
        (*(volatile uint16_t *)(h+0x5eu))--;
    }
    *rx_state=0x20u;
    return 0u;
}

#include <stdint.h>

extern uint32_t case_tick_word2(void);

static void clear_interrupt_bits(volatile uint32_t *reg,uint32_t mask)
{
    uint32_t previous,disabled=1u;
    __asm volatile("mrs %0, primask\nmsr primask, %1"
                   :"=&r"(previous):"r"(disabled):"memory");
    *reg &= ~mask;
    __asm volatile("msr primask, %0"::"r"(previous):"memory");
}

/* Original 0x08008ec4. The caller owns a live UART handle and peripheral.
 * HAL tick cadence and peripheral ISR evolution are separate contracts. */
/* Stock 0x08008EC4 (case_wait_condition) */
uint32_t case_wait_condition(void *handle,uint32_t flag,uint32_t expected,
                             uint32_t start,uint32_t timeout)
{
    volatile uint8_t *h=(volatile uint8_t *)handle;
    volatile uint32_t *peripheral=(volatile uint32_t *)(uintptr_t)
        (*(volatile uint32_t *)h);
    for(;;){
        uint32_t observed=(flag & ~peripheral[7])==0u;
        if(observed!=expected)return 0u;
        if(timeout==0xffffffffu)continue;
        uint32_t now=case_tick_word2();
        if(timeout<(uint32_t)(now-start) || timeout==0u)break;
        if((peripheral[0]&4u)!=0u && (peripheral[7]&0x800u)!=0u){
            peripheral[8]=0x800u;
            clear_interrupt_bits(&peripheral[0],0x1a0u);
            clear_interrupt_bits(&peripheral[2],1u);
            *(volatile uint32_t *)(h+0x88u)=0x20u;
            *(volatile uint32_t *)(h+0x8cu)=0x20u;
            *(volatile uint32_t *)(h+0x90u)=0x20u;
            *(volatile uint8_t *)(h+0x84u)=0u;
            return 3u;
        }
    }
    clear_interrupt_bits(&peripheral[0],0x1a0u);
    clear_interrupt_bits(&peripheral[2],1u);
    *(volatile uint32_t *)(h+0x88u)=0x20u;
    *(volatile uint32_t *)(h+0x8cu)=0x20u;
    *(volatile uint8_t *)(h+0x84u)=0u;
    return 3u;
}
